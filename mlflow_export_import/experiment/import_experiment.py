""" 
Exports an experiment to a directory.
"""

import os
import mlflow
import click
from mlflow_export_import import click_doc
from mlflow_export_import import peek_at_experiment
from mlflow_export_import.run.import_run import RunImporter
from mlflow_export_import import utils
from mlflow_export_import.common import mlflow_utils
from mlflow_export_import.common.http_client import DatabricksHttpClient

class ExperimentImporter():
    def __init__(self, mlflow_client=None, use_src_user_id=False, import_mlflow_tags=True, import_metadata_tags=False):
        self.mlflow_client = mlflow_client or mlflow.tracking.MlflowClient()
        self.run_importer = RunImporter(self.mlflow_client, use_src_user_id=use_src_user_id, import_mlflow_tags=import_mlflow_tags, import_metadata_tags=import_metadata_tags)
        print("MLflowClient:",self.mlflow_client)
        self.dbx_client = DatabricksHttpClient()

    def import_experiment(self, exp_name, input):
        self.import_experiment_from_dir(exp_name, input)

    def import_experiment_from_dir(self, exp_name, exp_dir):
        mlflow_utils.set_experiment(self.dbx_client, exp_name)
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
        utils.nested_tags(self.mlflow_client, run_ids_mapping)

@click.command()
@click.option("--input-dir", help="Input path - directory", required=True, type=str)
@click.option("--experiment-name", help="Destination experiment name", required=True, type=str)
@click.option("--just-peek", help="Just display experiment metadata - do not import", type=bool, default=False)
@click.option("--use-src-user-id", help=click_doc.use_src_user_id, type=bool, default=False)
@click.option("--import-mlflow-tags", help="Import mlflow tags", type=bool, default=True)
@click.option("--import-metadata-tags", help="Import mlflow_export_import tags", type=bool, default=False)

def main(input_dir, experiment_name, just_peek, use_src_user_id, import_mlflow_tags, import_metadata_tags): # pragma: no cover
    print("Options:")
    for k,v in locals().items():
        print(f"  {k}: {v}")
    if just_peek:
        peek_at_experiment(input_dir)
    else:
        importer = ExperimentImporter(None, use_src_user_id, import_mlflow_tags, import_metadata_tags)
        importer.import_experiment(experiment_name, input_dir)

if __name__ == "__main__":
    main()
