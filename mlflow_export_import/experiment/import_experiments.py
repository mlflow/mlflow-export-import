""" 
Exports an experiment to a directory.
"""

import os
import json
import mlflow
import click

from mlflow_export_import.run.import_run import RunImporter
from mlflow_export_import import utils, click_doc

class ExperimentImporter():
    def __init__(self, mlflow_client=None, use_src_user_id=False, import_mlflow_tags=True, import_metadata_tags=False):
        self.client = mlflow_client or mlflow.tracking.MlflowClient()
        self.run_importer = RunImporter(self.client, use_src_user_id=use_src_user_id, import_mlflow_tags=import_mlflow_tags, import_metadata_tags=import_metadata_tags)
        print("MLflowClient:",self.client)

    def import_experiment(self, exp_name, input):
        if input.endswith(".zip"):
            self.import_experiment_from_zip(exp_name, input)
        else:
            self.import_experiment_from_dir(exp_name, input)

    def import_experiment_from_dir(self, exp_name, exp_dir):
        mlflow.set_experiment(exp_name)
        manifest_path = os.path.join(exp_dir,"manifest.json")
        dct = utils.read_json_file(manifest_path)
        run_ids = dct["run_ids"]
        failed_run_ids = dct['failed_run_ids']
        print(f"Importing {len(run_ids)} runs into experiment '{exp_name}' from {exp_dir}")
        run_ids_mapping = {}
        for src_run_id in run_ids:
            dst_run_id, src_parent_run_id = self.run_importer.import_run(exp_name, os.path.join(exp_dir,src_run_id))
            run_ids_mapping[src_run_id] = (dst_run_id,src_parent_run_id)
        print(f"Imported {len(run_ids)} runs into experiment '{exp_name}' from {exp_dir}")
        if len(failed_run_ids) > 0:
            print(f"Warning: {len(failed_run_ids)} failed runs were not imported - see {manifest_path}")
        utils.nested_tags(self.client, run_ids_mapping)

    def import_experiment_from_zip(self, exp_name, zip_file):
        utils.unzip_directory(zip_file, exp_name, self.import_experiment_from_dir)

@click.command()
@click.option("--input-dir", help="Input directory.", required=True, type=str)
@click.option("--experiment-name-prefix", help="If specified, added as prefix to experiment name.", default=None, type=str, show_default=True)
@click.option("--use-src-user-id", help=click_doc.use_src_user_id, type=bool, default=False, show_default=True)
@click.option("--import-mlflow-tags", help=click_doc.import_mlflow_tags, type=bool, default=True, show_default=True)
@click.option("--import-metadata-tags", help=click_doc.import_metadata_tags, type=bool, default=False, show_default=True)

def main(input_dir, experiment_name_prefix, use_src_user_id, import_mlflow_tags, import_metadata_tags): # pragma: no cover
    print("Options:")
    for k,v in locals().items():
        print(f"  {k}: {v}")

    path = os.path.join(input_dir,"manifest.json")
    with open(path, "r") as f:
        dct = json.loads(f.read())
    for exp in dct["experiments"]:
        print("  ",exp)

    importer = ExperimentImporter(None, use_src_user_id, import_mlflow_tags, import_metadata_tags)
    for exp in dct["experiments"]:
        exp_input = os.path.join(input_dir,exp["id"])
        exp_name = experiment_name_prefix + exp["name"] if experiment_name_prefix else exp["name"]
        importer.import_experiment(exp_name, exp_input)

if __name__ == "__main__":
    main()
