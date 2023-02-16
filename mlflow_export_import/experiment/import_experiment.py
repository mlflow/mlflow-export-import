""" 
Exports an experiment to a directory.
"""

import os
import click
import mlflow

from mlflow_export_import.common import utils
from mlflow_export_import.common.click_options import *
from mlflow_export_import.common import io_utils
from mlflow_export_import.common import mlflow_utils
from mlflow_export_import.common.http_client import DatabricksHttpClient
from mlflow_export_import.run.import_run import RunImporter
from mlflow_export_import.common.source_tags import set_source_tags_for_field, mk_source_tags_mlflow_tag, fmt_timestamps


class ExperimentImporter():

    def __init__(self, mlflow_client, import_source_tags=False, mlmodel_fix=True, use_src_user_id=False):
        """
        :param mlflow_client: MLflow client.
        :param import_source_tags: Import source information for MLFlow objects and create tags in destination object.
        :param use_src_user_id: Set the destination user ID to the source user ID.
                                Source user ID is ignored when importing into
        """
        self.mlflow_client = mlflow_client
        self.run_importer = RunImporter(self.mlflow_client, 
            import_source_tags=import_source_tags,
            mlmodel_fix=mlmodel_fix,
            use_src_user_id=use_src_user_id,
            dst_notebook_dir_add_run_id=True)
        print("MLflowClient:", self.mlflow_client)
        self.dbx_client = DatabricksHttpClient()
        self.import_source_tags = import_source_tags


    def import_experiment(self, exp_name, input_dir, dst_notebook_dir=None):
        """
        :param: exp_name: Destination experiment name.
        :param: input_dir: Source experiment directory.
        :return: A map of source run IDs and destination run.info.
        """

        path = io_utils.mk_manifest_json_path(input_dir, "experiment.json")
        exp_dct = io_utils.read_file(path)
        info = io_utils.get_info(exp_dct)
        exp_dct = io_utils.get_mlflow(exp_dct)

        tags = exp_dct["experiment"]["tags"] 
        if self.import_source_tags:
            source_tags = mk_source_tags_mlflow_tag(tags)
            tags = { **tags, **source_tags }
            exp = exp_dct["experiment"]
            set_source_tags_for_field(exp, tags)
            fmt_timestamps("creation_time", exp, tags)
            fmt_timestamps("last_update_time", exp, tags)
        mlflow_utils.set_experiment(self.mlflow_client, self.dbx_client, exp_name, tags)

        run_ids = exp_dct["runs"]
        failed_run_ids = info["failed_runs"]

        print(f"Importing {len(run_ids)} runs into experiment '{exp_name}' from '{input_dir}'")
        run_ids_map = {}
        run_info_map = {}
        for src_run_id in run_ids:
            dst_run, src_parent_run_id = self.run_importer.import_run(exp_name, os.path.join(input_dir, src_run_id), dst_notebook_dir)
            dst_run_id = dst_run.info.run_id
            run_ids_map[src_run_id] = { "dst_run_id": dst_run_id, "src_parent_run_id": src_parent_run_id }
            run_info_map[src_run_id] = dst_run.info
        print(f"Imported {len(run_ids)} runs into experiment '{exp_name}' from '{input_dir}'")
        if len(failed_run_ids) > 0:
            print(f"Warning: {len(failed_run_ids)} failed runs were not imported - see '{path}'")
        utils.nested_tags(self.mlflow_client, run_ids_map)
        return run_info_map


@click.command()
@opt_experiment_name
@opt_input_dir
@opt_import_source_tags
@opt_use_src_user_id
@opt_dst_notebook_dir
def main(input_dir, experiment_name, import_source_tags, use_src_user_id, dst_notebook_dir):
    print("Options:")
    for k,v in locals().items():
        print(f"  {k}: {v}")
    else:
        client = mlflow.tracking.MlflowClient()
        importer = ExperimentImporter(
            client,
            import_source_tags=import_source_tags,
            use_src_user_id=use_src_user_id)
        importer.import_experiment(experiment_name, input_dir, dst_notebook_dir)


if __name__ == "__main__":
    main()
