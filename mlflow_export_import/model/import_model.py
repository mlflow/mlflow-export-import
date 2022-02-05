"""
Import a registered model and all the experiment runs associated with its latest versions.
"""

import os
import click
import mlflow
from mlflow.exceptions import RestException
from mlflow_export_import.run.import_run import RunImporter
from mlflow_export_import import utils, click_doc
from mlflow_export_import.common import model_utils

class BaseModelImporter():
    def __init__(self, run_importer=None, await_creation_for=None):
        self.client = mlflow.tracking.MlflowClient()
        self.run_importer = run_importer if run_importer else RunImporter(self.client, mlmodel_fix=True, import_mlflow_tags=False)
        self.await_creation_for = await_creation_for 

    def _import_version(self, model_name, src_vr, dst_run_id, sleep_time, dst_source):
        src_current_stage = src_vr["current_stage"]
        if not dst_source.startswith("dbfs:") and not os.path.exists(dst_source):
            raise Exception(f"'source' argument for MLflowClient.create_model_version does not exist: {dst_source}")
        kwargs = {"await_creation_for": self.await_creation_for } if self.await_creation_for else {}
        version = self.client.create_model_version(model_name, dst_source, dst_run_id, **kwargs)
        model_utils.wait_until_version_is_ready(self.client, model_name, version, sleep_time=sleep_time)
        if src_current_stage != "None":
            self.client.transition_model_version_stage(model_name, version.version, src_current_stage)

    def _import_model(self, input_dir, model_name, delete_model=False, verbose=False, sleep_time=30):
        path = os.path.join(input_dir,"model.json")
        model_dct = utils.read_json_file(path)["registered_model"]

        print("Model to import:")
        print(f"  Name: {model_dct['name']}")
        print(f"  Description: {model_dct.get('description','')}")
        print(f"  Tags: {model_dct.get('tags','')}")
        print(f"  {len(model_dct['latest_versions'])} latest versions")
        print(f"  path: {path}")

        if not model_name:
            model_name = model_dct["name"]
        if delete_model:
            model_utils.delete_model(self.client, model_name)

        try:
            tags = { e["key"]:e["value"] for e in model_dct.get("tags", {}) }
            self.client.create_registered_model(model_name, tags, model_dct.get("description"))
            print(f"Created new registered model '{model_name}'")
        except RestException as e:
            if not "RESOURCE_ALREADY_EXISTS: Registered Model" in str(e):
                raise e
            print(f"Registered model '{model_name}' already exists")
        return model_dct

class ModelImporter(BaseModelImporter):
    """ Low-level 'point' model importer  """
    def __init__(self, run_importer=None, await_creation_for=None):
        super().__init__(run_importer, await_creation_for)

    def import_model(self, input_dir, model_name, experiment_name, delete_model=False, verbose=False, sleep_time=30):
        model_dct = self._import_model(input_dir, model_name, delete_model, verbose, sleep_time)
        mlflow.set_experiment(experiment_name)
        print("Importing versions:")
        for vr in model_dct["latest_versions"]:
            run_id = self.import_run(input_dir, experiment_name, vr)
            self.import_version(model_name, vr, run_id, sleep_time)
        if verbose:
            model_utils.dump_model_versions(self.client, model_name)

    def import_run(self, input_dir, experiment_name, vr):
        run_id = vr["run_id"]
        source = vr["source"]
        current_stage = vr["current_stage"]
        run_artifact_uri = vr.get("_run_artifact_uri",None)
        run_dir = os.path.join(input_dir,run_id)
        print(f"  Version {vr['version']}:")
        print(f"    current_stage: {current_stage}:")
        print(f"    Source run - run to import:")
        print(f"      run_id: {run_id}")
        print(f"      run_artifact_uri: {run_artifact_uri}")
        print(f"      source:           {source}")
        model_path = extract_model_path(source, run_id)
        print(f"      model_path:   {model_path}")
        dst_run,_ = self.run_importer.import_run(experiment_name, run_dir)
        dst_run_id = dst_run.info.run_id
        run = self.client.get_run(dst_run_id)
        print(f"    Destination run - imported run:")
        print(f"      run_id: {dst_run_id}")
        print(f"      run_artifact_uri: {run.info.artifact_uri}")
        source = path_join(run.info.artifact_uri, model_path)
        print(f"      source:           {source}")
        return dst_run_id

    def import_version(self, model_name, src_vr, dst_run_id, sleep_time):
        dst_run = self.client.get_run(dst_run_id)
        model_path = extract_model_path(src_vr["source"], src_vr["run_id"])
        dst_source = f"{dst_run.info.artifact_uri}/{model_path}"
        self._import_version(model_name, src_vr, dst_run_id, sleep_time, dst_source)

class AllModelImporter(BaseModelImporter):
    """ High-level 'bulk' model importer  """
    def __init__(self, run_info_map, run_importer=None, await_creation_for=None):
        super().__init__(run_importer, await_creation_for)
        self.run_info_map = run_info_map

    def import_model(self, input_dir, model_name, delete_model=False, verbose=False, sleep_time=30):
        model_dct = self._import_model(input_dir, model_name, delete_model, verbose, sleep_time)
        print("Importing latest versions:")
        for vr in model_dct["latest_versions"]:
            src_run_id = vr["run_id"]
            dst_run_id = self.run_info_map[src_run_id].run_id
            mlflow.set_experiment(vr["_experiment_name"])
            self.import_version(model_name, vr, dst_run_id, sleep_time)
        if verbose:
            model_utils.dump_model_versions(self.client, model_name)

    def import_version(self, model_name, src_vr, dst_run_id, sleep_time):
        src_run_id = src_vr["run_id"]
        model_path = extract_model_path(src_vr["source"], src_run_id)
        dst_artifact_uri = self.run_info_map[src_run_id].artifact_uri
        dst_source = f"{dst_artifact_uri}/{model_path}"
        self._import_version(model_name, src_vr, dst_run_id, sleep_time, dst_source)


def extract_model_path(source, run_id):
    idx = source.find(run_id)
    model_path = source[1+idx+len(run_id):]
    if model_path.startswith("artifacts/"): # Bizarre - sometimes there is no 'artifacts' after run_id
        model_path = model_path.replace("artifacts/","")
    return model_path

def path_join(x,y):
    """ Account for DOS backslash """
    path = os.path.join(x,y)
    if path.startswith("dbfs:"):
        path = path.replace("\\","/") 
    return path

@click.command()
@click.option("--input-dir", 
    help="Input directory produced by export_model.py.", 
    type=str,
    required=True
)
@click.option("--model", 
    help="New registered model name.", 
    type=str,
    required=True, 
)
@click.option("--experiment-name", 
    help="Destination experiment name  - will be created if it does not exist.", 
    type=str,
    required=True
)
@click.option("--delete-model", 
    help=click_doc.delete_model, 
    type=bool,
    default=False, 
    show_default=True
)
@click.option("--await-creation-for", 
    help="Await creation for specified seconds.", 
    type=int, 
    default=None, 
    show_default=True
)
@click.option("--sleep-time", 
    help="Sleep time for polling until version.status==READY.", 
    type=int,
    default=5,
)
@click.option("--verbose", 
    help="Verbose.", 
    type=bool, 
    default=False, 
    show_default=True
)

def main(input_dir, model, experiment_name, delete_model, await_creation_for, verbose, sleep_time): # pragma: no cover
    print("Options:")
    for k,v in locals().items():
        print(f"  {k}: {v}")
    importer = ModelImporter(await_creation_for=await_creation_for)
    importer.import_model(input_dir, model, experiment_name, delete_model, verbose, sleep_time)

if __name__ == "__main__":
    main()
