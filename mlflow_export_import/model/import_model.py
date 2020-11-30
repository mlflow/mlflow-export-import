"""
Import a registered model and all the experiment runs associated with its latest versions.
"""

import os
import click
import mlflow
from mlflow_export_import.run.import_run import RunImporter
from mlflow_export_import import utils
from mlflow_export_import.common import model_utils
from mlflow_export_import.common import filesystem as _filesystem

class ModelImporter():
    def __init__(self, filesystem=None):
        self.fs = filesystem or _filesystem.get_filesystem()
        self.client = mlflow.tracking.MlflowClient()
        self.run_importer = RunImporter(self.client)

    def import_model(self, input_dir, model_name, experiment_name, delete_model=False):
        path = os.path.join(input_dir,"model.json")
        dct = utils.read_json_file(path)
        dct = dct["registered_model"]

        print("Model to import:")
        print(f"  Name: {dct['name']}")
        print(f"  Description: {dct.get('description','')}")
        print(f"  Tags: {dct.get('tags','')}")
        print(f"  {len(dct['latest_versions'])} latest versions")

        if delete_model:
            model_utils.delete_model(self.client, model_name)

        tags = { e["key"]:e["value"] for e in dct.get("tags", {}) }
        self.client.create_registered_model(model_name, tags, dct.get("description"))
        mlflow.set_experiment(experiment_name)

        print("Importing latest versions:")
        for v in dct["latest_versions"]:
            run_id = v["run_id"]
            source = v["source"]
            current_stage = v["current_stage"]
            artifact_uri = v["artifact_uri"]
            run_dir = os.path.join(input_dir,run_id)
            print(f"  Version {v['version']}:")
            print(f"    current_stage: {v['current_stage']}:")
            print("    Run to import:")
            print("      run_id:", run_id)
            print("      artifact_uri:", artifact_uri)
            print("      source:      ", source)
            model_path = source.replace(artifact_uri+"/","")
            print("      model_path:", model_path)
            print("      run_id:",run_id)
            run_id,_ = self.run_importer.import_run(experiment_name, run_dir)
            run = self.client.get_run(run_id)
            print("    Imported run:")
            print("      run_id:", run_id)
            print("      artifact_uri:", run.info.artifact_uri)
            source = os.path.join(run.info.artifact_uri,model_path)
            print("      source:      ", source)

            version = self.client.create_model_version(model_name, source, run_id)
            model_utils.wait_until_version_is_ready(self.client, model_name, version, sleep_time=2)
            self.client.transition_model_version_stage(model_name, version.version, current_stage)

@click.command()
@click.option("--input-dir", help="Input directory produced by export_model.py.", required=True, type=str)
@click.option("--model", help="New registered model name.", required=True, type=str)
@click.option("--experiment-name", help="Destination experiment name  - will be created if it does not exist.", required=True, type=str)
@click.option("--delete-model", help="First delete the model if it exists and all its versions.", type=bool, default=False, show_default=True)

def main(input_dir, model, experiment_name, delete_model): # pragma: no cover
    print("Options:")
    for k,v in locals().items():
        print(f"  {k}: {v}")
    importer = ModelImporter()
    importer.import_model(input_dir, model, experiment_name, delete_model)

if __name__ == "__main__":
    main()
