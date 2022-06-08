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
    def __init__(self, mlflow_client, mlmodel_fix=True, use_src_user_id=False):
        """
        :param mlflow_client: MLflow client.
        :param use_src_user_id: Set the destination user ID to the source user ID.
                                Source user ID is ignored when importing into
        """
        self.mlflow_client = mlflow_client
        self.run_importer = RunImporter(self.mlflow_client, mlmodel_fix=mlmodel_fix, \
            use_src_user_id=use_src_user_id, \
            dst_notebook_dir_add_run_id=True)
        print("MLflowClient:",self.mlflow_client)
        self.dbx_client = DatabricksHttpClient()

    def import_experiment(self, exp_name, input_dir, dst_notebook_dir=None):
        """
        :param: exp_name: Destination experiment name.
        :param: input_dir: Source experiment directory.
        :return: A map of source run IDs and destination run.info.
        """
        mlflow_utils.set_experiment(self.mlflow_client, self.dbx_client, exp_name)
        manifest_path = os.path.join(input_dir,"manifest.json")
        dct = utils.read_json_file(manifest_path)
        run_ids = dct["export_info"]["ok_runs"]
        failed_run_ids = dct["export_info"]["failed_runs"]
        print(f"Importing {len(run_ids)} runs into experiment '{exp_name}' from {input_dir}")
        run_ids_map = {}
        run_info_map = {}
        for src_run_id in run_ids:
            dst_run, src_parent_run_id = self.run_importer.import_run(exp_name, os.path.join(input_dir,src_run_id), dst_notebook_dir)
            dst_run_id = dst_run.info.run_id
            run_ids_map[src_run_id] = { "dst_run_id": dst_run_id, "src_parent_run_id": src_parent_run_id }
            run_info_map[src_run_id] = dst_run.info
        print(f"Imported {len(run_ids)} runs into experiment '{exp_name}' from {input_dir}")
        if len(failed_run_ids) > 0:
            print(f"Warning: {len(failed_run_ids)} failed runs were not imported - see {manifest_path}")
        utils.nested_tags(self.mlflow_client, run_ids_map)
        return run_info_map


@click.command()
@click.option("--input-dir", 
    help="Input path - directory", 
    type=str,
    required=True
)
@click.option("--experiment-name", 
    help="Destination experiment name", 
    type=str,
    required=True
)
@click.option("--just-peek", 
    help="Just display experiment metadata - do not import", 
    type=bool, 
    default=False
)
@click.option("--use-src-user-id", 
    help=click_doc.use_src_user_id, 
    type=bool, 
    default=False
)
@click.option("--dst-notebook-dir",
    help="Databricks destination workpsace base directory for notebook. A run ID will be added to contain the run's notebook.",
    type=str,
    required=False,
    show_default=True
)

def main(input_dir, experiment_name, just_peek, use_src_user_id, dst_notebook_dir):
    print("Options:")
    for k,v in locals().items():
        print(f"  {k}: {v}")
    if just_peek:
        peek_at_experiment(input_dir)
    else:
        client = mlflow.tracking.MlflowClient()
        importer = ExperimentImporter(
            client,
            use_src_user_id=use_src_user_id)
        importer.import_experiment(experiment_name, input_dir, dst_notebook_dir)

if __name__ == "__main__":
    main()
