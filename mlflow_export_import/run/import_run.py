"""
Imports a run from a directory.
"""

import os
import time
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
        :param exp_name: Experiment name
        :param input_dir: Source input directory that contains the exported run.
        """
        print(f"Importing run from '{input_dir}'")
        res = self._import_run(exp_name, input_dir)
        print(f"Imported run into '{exp_name}/{res[0]}'")
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
            
        return (run_id, src_run_dct["tags"].get(utils.TAG_PARENT_ID,None))

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

    def _dump_tags(self, tags, msg=""):
        print(f"Tags {msg} - {len(tags)}:")
        for t in tags: print(f"  {t.key} - {t.value}")

    def _import_run_data(self, run_dct, run_id, src_user_id):
        from mlflow.entities import Metric, Param, RunTag
        now = round(time.time())
        params = [ Param(k,v) for k,v in run_dct["params"].items() ]
        metrics = [ Metric(k,v,now,0) for k,v in run_dct["metrics"].items() ] # TODO: missing timestamp and step semantics?

        tags = run_dct["tags"]
        if not self.import_mlflow_tags: # remove mlflow tags
            tags = { k:v for k,v in tags.items() if not k.startswith(utils.TAG_PREFIX_MLFLOW) }
        if not self.import_metadata_tags: # remove mlflow_export_import tags
            tags = { k:v for k,v in tags.items() if not k.startswith(utils.TAG_PREFIX_METADATA) }
        tags = utils.create_mlflow_tags_for_databricks_import(tags) # remove "mlflow" tags that cannot be imported into Databricks

        tags = [ RunTag(k,str(v)) for k,v in tags.items() ]

        #self._dump_tags(tags,"1") # debug
        if not self.in_databricks:
            utils.set_dst_user_id(tags, src_user_id, self.use_src_user_id)
        #self._dump_tags(tags,"2") # debug
        self.mlflow_client.log_batch(run_id, metrics, params, tags)

@click.command()
@click.option("--input-dir", help="Source input directory that contains the exported run.", required=True, type=str)
@click.option("--experiment-name", help="Destination experiment name.", required=True, type=str)
@click.option("--mlmodel-fix", help="Add correct run ID in destination MLmodel artifact. Can be expensive for deeply nested artifacts.", type=bool, default=True, show_default=True)
@click.option("--use-src-user-id", help=click_doc.use_src_user_id, type=bool, default=False, show_default=True)
@click.option("--import-mlflow-tags", help=click_doc.import_mlflow_tags, type=bool, default=False, show_default=True)
@click.option("--import-metadata-tags", help=click_doc.import_metadata_tags, type=bool, default=False, show_default=True)

def main(input_dir, experiment_name, mlmodel_fix, use_src_user_id, import_mlflow_tags, import_metadata_tags): # pragma: no cover
    print("Options:")
    for k,v in locals().items():
        print(f"  {k}: {v}")
    importer = RunImporter(None, mlmodel_fix, use_src_user_id, import_mlflow_tags, import_metadata_tags)
    importer.import_run(experiment_name, input_dir)

if __name__ == "__main__":
    main()
