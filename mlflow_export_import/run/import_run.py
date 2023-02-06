"""
Imports a run from a directory.
"""

import os
import tempfile
import click
import base64

import mlflow
from mlflow.entities import RunStatus
from mlflow.utils.validation import MAX_PARAMS_TAGS_PER_BATCH, MAX_METRICS_PER_BATCH
from mlflow.utils.mlflow_tags import MLFLOW_PARENT_RUN_ID

from mlflow_export_import.common import utils

from mlflow_export_import.common.click_options import opt_input_dir, opt_import_source_tags,\
  opt_experiment_name, opt_use_src_user_id, opt_dst_notebook_dir

from mlflow_export_import.common.filesystem import mk_local_path
from mlflow_export_import.common.find_artifacts import find_artifacts
from mlflow_export_import.common.http_client import DatabricksHttpClient
from mlflow_export_import.common import mlflow_utils
from mlflow_export_import.common import io_utils
from mlflow_export_import.common import filesystem as _filesystem
from mlflow_export_import.common import MlflowExportImportException
from mlflow_export_import.run import run_data_importer


class RunImporter():
    def __init__(self, 
            mlflow_client, 
            import_source_tags=False,
            mlmodel_fix=True, 
            use_src_user_id=False, \
            dst_notebook_dir_add_run_id=False):
        """ 
        :param mlflow_client: MLflow client.
        :param import_source_tags: Import source information for MLFlow objects and create tags in destination object.
        :param mlmodel_fix: Add correct run ID in destination MLmodel artifact. 
                            Can be expensive for deeply nested artifacts.
        :param use_src_user_id: Set the destination user ID to the source user ID. 
                                Source user ID is ignored when importing into 
                                Databricks since setting it is not allowed.
        :param dst_notebook_dir: Databricks destination workspace directory for notebook import.
        :param dst_notebook_dir_add_run_id: Add the run ID to the destination notebook directory.
        """

        self.mlflow_client = mlflow_client
        self.mlmodel_fix = mlmodel_fix
        self.use_src_user_id = use_src_user_id
        self.in_databricks = "DATABRICKS_RUNTIME_VERSION" in os.environ
        self.dst_notebook_dir_add_run_id = dst_notebook_dir_add_run_id
        self.dbx_client = DatabricksHttpClient()
        self.import_source_tags = import_source_tags
        print(f"in_databricks: {self.in_databricks}")
        print(f"importing_into_databricks: {utils.importing_into_databricks()}")


    def import_run(self, exp_name, input_dir, dst_notebook_dir=None):
        """ 
        Imports a run into the specified experiment.
        :param exp_name: Experiment name.
        :param input_dir: Source input directory that contains the exported run.
        :param dst_notebook_dir: Databricks destination workpsace directory for notebook.
        :return: The run and its parent run ID if the run is a nested run.
        """
        print(f"Importing run from '{input_dir}'")
        res = self._import_run(exp_name, input_dir, dst_notebook_dir)
        print(f"Imported run into '{exp_name}/{res[0].info.run_id}'")
        return res


    def _import_run(self, dst_exp_name, input_dir, dst_notebook_dir):
        exp_id = mlflow_utils.set_experiment(self.mlflow_client, self.dbx_client, dst_exp_name)
        exp = self.mlflow_client.get_experiment(exp_id)
        src_run_path = os.path.join(input_dir,"run.json")
        src_run_dct = io_utils.read_file_mlflow(src_run_path)

        run = self.mlflow_client.create_run(exp.experiment_id)
        run_id = run.info.run_id
        try:
            self._import_run_data(src_run_dct, run_id, src_run_dct["info"]["user_id"])
            path = os.path.join(input_dir, "artifacts")
            if os.path.exists(_filesystem.mk_local_path(path)):
                self.mlflow_client.log_artifacts(run_id, mk_local_path(path))
            if self.mlmodel_fix:
                self._update_mlmodel_run_id(run_id)
            self.mlflow_client.set_terminated(run_id, RunStatus.to_string(RunStatus.FINISHED))
            run = self.mlflow_client.get_run(run_id)
        except Exception as e:
            self.mlflow_client.set_terminated(run_id, RunStatus.to_string(RunStatus.FAILED))
            import traceback
            traceback.print_exc()
            raise MlflowExportImportException from e
        if utils.importing_into_databricks() and dst_notebook_dir:
            ndir = os.path.join(dst_notebook_dir, run_id) if self.dst_notebook_dir_add_run_id else dst_notebook_dir
            self._upload_databricks_notebook(input_dir, src_run_dct, ndir)

        return (run, src_run_dct["tags"].get(MLFLOW_PARENT_RUN_ID,None))


    def _update_mlmodel_run_id(self, run_id):
        """ 
        Workaround to fix the run_id in the destination MLmodel file since there is no method to get all model artifacts of a run.

        Since an MLflow run does not keeps track of its models, there is no method to retrieve the artifact path to all its models.
        This workaround recursively searches the run's root artifact directory for all MLmodel files, and assumes their directory
        represents a path to the model.
        """

        mlmodel_paths = find_artifacts(run_id, "", "MLmodel")
        for mlmodel_path in mlmodel_paths:
            model_path = mlmodel_path.replace("/MLmodel","")
            local_path = self.mlflow_client.download_artifacts(run_id, mlmodel_path)
            mlmodel = io_utils.read_file(local_path, "yaml")
            mlmodel["run_id"] = run_id
            with tempfile.TemporaryDirectory() as dir:
                output_path = os.path.join(dir, "MLmodel")
                io_utils.write_file(output_path, mlmodel, "yaml")
                if model_path == "MLmodel":
                    model_path = ""
                self.mlflow_client.log_artifact(run_id, output_path, model_path)


    def _import_run_data(self, run_dct, run_id, src_user_id):
        run_data_importer.log_params(self.mlflow_client, run_dct, run_id, MAX_PARAMS_TAGS_PER_BATCH)
        run_data_importer.log_metrics(self.mlflow_client, run_dct, run_id, MAX_METRICS_PER_BATCH)
        run_data_importer.log_tags(
            self.mlflow_client, 
            run_dct, 
            run_id, 
            MAX_PARAMS_TAGS_PER_BATCH, 
            self.import_source_tags,
            self.in_databricks, 
            src_user_id, 
            self.use_src_user_id
    )


    def _upload_databricks_notebook(self, input_dir, src_run_dct, dst_notebook_dir):
        run_id = src_run_dct["info"]["run_id"]
        tag_key = "mlflow.databricks.notebookPath"
        src_notebook_path = src_run_dct["tags"].get(tag_key,None)
        if not src_notebook_path:
            print(f"WARNING: No tag '{tag_key}' for run_id '{run_id}'")
            return
        notebook_name = os.path.basename(src_notebook_path)

        format = "source" 
        notebook_path = os.path.join(input_dir,"artifacts","notebooks",f"{notebook_name}.{format}")
        if not os.path.exists(notebook_path): 
            print(f"WARNING: Source '{notebook_path}' does not exist for run_id '{run_id}'")
            return

        with open(notebook_path, "r", encoding="utf-8") as f:
            content = f.read()
        dst_notebook_path = os.path.join(dst_notebook_dir,notebook_name)
        content = base64.b64encode(content.encode()).decode("utf-8")
        data = {
            "path": dst_notebook_path,
            "language": "PYTHON",
            "format": format,
            "overwrite": True,
            "content": content
            }
        mlflow_utils.create_workspace_dir(self.dbx_client, dst_notebook_dir)
        try:
            print(f"Importing notebook '{dst_notebook_path}' for run {run_id}")
            self.dbx_client._post("workspace/import", data)
        except MlflowExportImportException as e:
            print(f"WARNING: Cannot save notebook '{dst_notebook_path}'. {e}")


@click.command()
@opt_input_dir
@opt_import_source_tags
@opt_experiment_name
@opt_use_src_user_id
@opt_dst_notebook_dir
@click.option("--mlmodel-fix",
    help="Add correct run ID in destination MLmodel artifact. Can be expensive for deeply nested artifacts.", 
    type=bool, 
    default=True, 
    show_default=True
)
@click.option("--dst-notebook-dir-add-run-id",
    help="Add the run ID to the destination notebook workspace directory.",
    type=str,
    required=False,
    show_default=True
)
def main(input_dir, 
        experiment_name, 
        import_source_tags,
        mlmodel_fix, 
        use_src_user_id,
        dst_notebook_dir, 
        dst_notebook_dir_add_run_id):
    print("Options:")
    for k,v in locals().items():
        print(f"  {k}: {v}")
    client = mlflow.tracking.MlflowClient()
    importer = RunImporter(
        client,
        import_source_tags=import_source_tags,
        mlmodel_fix=mlmodel_fix, 
        use_src_user_id=use_src_user_id, 
        dst_notebook_dir_add_run_id=dst_notebook_dir_add_run_id)
    importer.import_run(experiment_name, input_dir, dst_notebook_dir)


if __name__ == "__main__":
    main()
