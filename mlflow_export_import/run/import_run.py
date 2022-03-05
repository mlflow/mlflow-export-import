"""
Imports a run from a directory.
"""

import os
import yaml
import tempfile
import click
import mlflow
from mlflow.entities import RunStatus

from mlflow_export_import import utils, click_doc
from mlflow_export_import import mk_local_path
from mlflow_export_import.common.find_artifacts import find_artifacts
from mlflow_export_import.common.http_client import DatabricksHttpClient
from mlflow_export_import.common import mlflow_utils
from mlflow_export_import.common import filesystem as _filesystem
from mlflow_export_import.run import run_data_importer
from mlflow.utils.validation import MAX_PARAMS_TAGS_PER_BATCH, MAX_METRICS_PER_BATCH


class RunImporter():
    def __init__(self, mlflow_client=None, mlmodel_fix=True, use_src_user_id=False, import_mlflow_tags=False, import_metadata_tags=False):
        """ 
        :param mlflow_client: MLflow client or if None create default client.
        :param mlmodel_fix: Add correct run ID in destination MLmodel artifact. 
                            Can be expensive for deeply nested artifacts.
        :param use_src_user_id: Set the destination user ID to the source user ID. 
                                Source user ID is ignored when importing into 
                                Databricks since setting it is not allowed.
        :param import_mlflow_tags: Import mlflow tags.
        :param import_metadata_tags: Import mlflow_export_import tags.
        """
        self.mlflow_client = mlflow_client or mlflow.tracking.MlflowClient()
        self.mlmodel_fix = mlmodel_fix
        self.use_src_user_id = use_src_user_id
        self.import_mlflow_tags = import_mlflow_tags
        self.import_metadata_tags = import_metadata_tags
        self.in_databricks = "DATABRICKS_RUNTIME_VERSION" in os.environ
        self.dbx_client = DatabricksHttpClient()
        print(f"in_databricks: {self.in_databricks}")
        print(f"importing_into_databricks: {utils.importing_into_databricks()}")

    def import_run(self, exp_name, input_dir):
        """ 
        Imports a run into the specified experiment.
        :param exp_name: Experiment name.
        :param input_dir: Source input directory that contains the exported run.
        :return: The run and its parent run ID if the run is a nested run.
        """
        print(f"Importing run from '{input_dir}'")
        res = self._import_run(exp_name, input_dir)
        print(f"Imported run into '{exp_name}/{res[0].info.run_id}'")
        return res

    def _import_run(self, dst_exp_name, src_run_id):
        mlflow_utils.set_experiment(self.dbx_client, dst_exp_name)
        exp = self.mlflow_client.get_experiment_by_name(dst_exp_name)
        src_run_path = os.path.join(src_run_id,"run.json")
        src_run_dct = utils.read_json_file(src_run_path)

        run = self.mlflow_client.create_run(exp.experiment_id)
        run_id = run.info.run_id
        try:
            self._import_run_data(src_run_dct, run_id, src_run_dct["info"]["user_id"])
            path = os.path.join(src_run_id,"artifacts")
            if os.path.exists(_filesystem.mk_local_path(path)):
                self.mlflow_client.log_artifacts(run_id, mk_local_path(path))
            if self.mlmodel_fix:
                self._update_mlmodel_run_id(run_id)
            self.mlflow_client.set_terminated(run_id, RunStatus.to_string(RunStatus.FINISHED))
        except Exception as e:
            self.mlflow_client.set_terminated(run_id, RunStatus.to_string(RunStatus.FAILED))
            import traceback
            from mlflow_export_import.common import MlflowExportImportException
            traceback.print_exc()
            raise MlflowExportImportException from e
            
        return (run, src_run_dct["tags"].get(utils.TAG_PARENT_ID,None))

    def _update_mlmodel_run_id(self, run_id):
        """ Patch to fix the run_id in the destination MLmodel file since there is no API to get all model artifacts of a run. """
        mlmodel_paths = find_artifacts(run_id, "", "MLmodel")
        for mlmodel_path in mlmodel_paths:
            model_path = mlmodel_path.replace("/MLmodel","")
            local_path = self.mlflow_client.download_artifacts(run_id, mlmodel_path)
            with open(local_path, "r") as f:
                mlmodel = yaml.safe_load(f)
            mlmodel["run_id"] = run_id
            with tempfile.TemporaryDirectory() as dir:
                output_path = os.path.join(dir, "MLmodel")
                with open(output_path, "w") as f:
                    yaml.dump(mlmodel, f)
                self.mlflow_client.log_artifact(run_id, output_path,  f"{model_path}")

    def _import_run_data(self, run_dct, run_id, src_user_id):
        run_data_importer.log_params(self.mlflow_client, run_dct, run_id, MAX_PARAMS_TAGS_PER_BATCH)
        run_data_importer.log_metrics(self.mlflow_client, run_dct, run_id, MAX_METRICS_PER_BATCH)
        run_data_importer.log_tags(
            self.mlflow_client, 
            run_dct, 
            run_id, 
            MAX_PARAMS_TAGS_PER_BATCH, 
            self.import_mlflow_tags, 
            self.import_metadata_tags, 
            self.in_databricks, 
            src_user_id, 
            self.use_src_user_id)


@click.command()
@click.option("--input-dir",
    help="Source input directory that contains the exported run.", 
    required=True, 
    type=str
)
@click.option("--experiment-name",
    help="Destination experiment name.", 
    type=str,
    required=True
)
@click.option("--mlmodel-fix",
    help="Add correct run ID in destination MLmodel artifact. Can be expensive for deeply nested artifacts.", 
    type=bool, 
    default=True, 
    show_default=True
)
@click.option("--use-src-user-id",
    help=click_doc.use_src_user_id, 
    type=bool, 
    default=False, 
    show_default=True
)
@click.option("--import-mlflow-tags",
    help=click_doc.import_mlflow_tags, 
    type=bool, 
    default=False, 
    show_default=True
)
@click.option("--import-metadata-tags",
    help=click_doc.import_metadata_tags, 
    type=bool, 
    default=False, 
    show_default=True
)

def main(input_dir, experiment_name, mlmodel_fix, use_src_user_id, import_mlflow_tags, import_metadata_tags): # pragma: no cover
    print("Options:")
    for k,v in locals().items():
        print(f"  {k}: {v}")
    importer = RunImporter(None, mlmodel_fix, use_src_user_id, import_mlflow_tags, import_metadata_tags)
    importer.import_run(experiment_name, input_dir)

if __name__ == "__main__":
    main()
