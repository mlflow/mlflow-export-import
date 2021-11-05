"""
Import a registered model and all the experiment runs associated with its latest versions.
"""

import os
import click
import mlflow
from mlflow.exceptions import RestException
from mlflow_export_import.run.import_run import RunImporter
from mlflow_export_import import utils
from mlflow_export_import.common import model_utils
from mlflow_export_import.common import filesystem as _filesystem

class ModelImporter():
    def __init__(self, filesystem=None, run_importer=None, await_creation_for=None):
        self.fs = filesystem or _filesystem.get_filesystem()
        self.client = mlflow.tracking.MlflowClient()
        self.run_importer = run_importer if run_importer else RunImporter(self.client, mlmodel_fix=True, import_mlflow_tags=False)
        self.await_creation_for = await_creation_for 

    def import_model(self, input_dir, model_name, experiment_name, delete_model=False, verbose=False):
        path = os.path.join(input_dir,"model.json")
        dct = utils.read_json_file(path)
        dct = dct["registered_model"]

        print("Model to import:")
        print(f"  Name: {dct['name']}")
        print(f"  Description: {dct.get('description','')}")
        print(f"  Tags: {dct.get('tags','')}")
        print(f"  {len(dct['latest_versions'])} latest versions")
        print(f"  path: {path}")

        if not model_name:
            model_name = dct["name"]
        if delete_model:
            model_utils.delete_model(self.client, model_name)

        try:
            tags = { e["key"]:e["value"] for e in dct.get("tags", {}) }
            self.client.create_registered_model(model_name, tags, dct.get("description"))
        except RestException as e:
            if not "RESOURCE_ALREADY_EXISTS: Registered Model" in str(e):
                raise e
        mlflow.set_experiment(experiment_name)

        print("Importing latest versions:")

        for vr in dct["latest_versions"]:
            self.import_run(input_dir, experiment_name, vr)
            self.import_version(model_name, vr)

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
        run_id,_ = self.run_importer.import_run(experiment_name, run_dir)
        run = self.client.get_run(run_id)
        print(f"    Destination run - imported run:")
        print(f"      run_id: {run_id}")
        print(f"      run_artifact_uri: {run.info.artifact_uri}")
        source = path_join(run.info.artifact_uri,model_path)
        print(f"      source:           {source}")

    def import_version(self, model_name, vr):
        source = vr["source"]
        current_stage = vr["current_stage"]
        if not source.startswith("dbfs:") and not os.path.exists(source):
            raise Exception(f"'source' argument for MLflowClient.create_model_version does not exist: {source}")
        kwargs = {"await_creation_for": self.await_creation_for } if self.await_creation_for else {}
        version = self.client.create_model_version(model_name, source, vr["run_id"], **kwargs)
        model_utils.wait_until_version_is_ready(self.client, model_name, version, sleep_time=2)
        if current_stage != "None":
            self.client.transition_model_version_stage(model_name, version.version, current_stage)

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
@click.option("--input-dir", help="Input directory produced by export_model.py.", required=True, type=str)
@click.option("--model", help="New registered model name.", required=True, type=str)
@click.option("--experiment-name", help="Destination experiment name  - will be created if it does not exist.", required=True, type=str)
@click.option("--delete-model", help="First delete the model if it exists and all its versions.", type=bool, default=False, show_default=True)
@click.option("--await-creation-for", help="Await creation for specified seconds.", type=int, default=None, show_default=True)
@click.option("--verbose", help="Verbose.", type=bool, default=False, show_default=True)

def main(input_dir, model, experiment_name, delete_model, await_creation_for, verbose): # pragma: no cover
    print("Options:")
    for k,v in locals().items():
        print(f"  {k}: {v}")
    importer = ModelImporter(await_creation_for=await_creation_for)
    importer.import_model(input_dir, model, experiment_name, delete_model, verbose)

if __name__ == "__main__":
    main()
