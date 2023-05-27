"""
Import a registered model and all the runs associated with each version.
"""

import os
import click

import mlflow
from mlflow.exceptions import RestException

from mlflow_export_import.common.click_options import (
    opt_input_dir,
    opt_model,
    opt_experiment_name,
    opt_import_permissions,
    opt_delete_model,
    opt_import_source_tags,
    opt_verbose
)
from mlflow_export_import.common import utils, io_utils, model_utils
from mlflow_export_import.common.source_tags import set_source_tags_for_field, fmt_timestamps
from mlflow_export_import.common import MlflowExportImportException
from mlflow_export_import.common.permissions_utils import import_permissions
from mlflow_export_import.client.http_client import DatabricksHttpClient
from mlflow_export_import.run.import_run import import_run
from mlflow_export_import.bulk import rename_utils

_logger = utils.getLogger(__name__)


def _set_source_tags_for_field(dct, tags):
    set_source_tags_for_field(dct, tags)
    fmt_timestamps("creation_timestamp", dct, tags)
    fmt_timestamps("last_updated_timestamp", dct, tags)


def import_model(
        model_name,
        experiment_name,
        input_dir,
        delete_model = False,
        import_permissions = False,
        import_source_tags = False,
        verbose=False,
        await_creation_for = None,
        sleep_time = 30,
        mlflow_client = None
    ):
    importer = ModelImporter(
        import_source_tags = import_source_tags,
        import_permissions = import_permissions,
        await_creation_for = await_creation_for,
        mlflow_client = mlflow_client
    )
    return importer.import_model(
        model_name = model_name,
        input_dir = input_dir,
        experiment_name = experiment_name,
        delete_model = delete_model,
        verbose = verbose,
        sleep_time = sleep_time
    )


class BaseModelImporter():
    """ Base class of ModelImporter subclasses. """

    def __init__(self,
            mlflow_client = None,
            import_permissions = False,
            import_source_tags = False,
            await_creation_for = None
        ):
        """
        :param mlflow_client: MLflow client or if None create default client.
        :param import_permissions: Import Databricks permissions.
        :param import_source_tags: Import source information for MLFlow objects and create tags in destination object.
        :param await_creation_for: Seconds to wait for model version crreation.
        """
        self.mlflow_client = mlflow_client or mlflow.MlflowClient()
        self.dbx_client = DatabricksHttpClient(self.mlflow_client.tracking_uri)
        self.import_source_tags=import_source_tags
        self.import_permissions = import_permissions 
        self.import_source_tags = import_source_tags 
        self.await_creation_for = await_creation_for 


    def _import_version(self,
            model_name,
            src_vr,
            dst_run_id,
            dst_source,
            sleep_time
        ):
        """
        :param model_name: Model name.
        :param src_vr: Source model version.
        :param dst_run: Destination run.
        :param dst_source: Destination version 'source' field.
        :param sleep_time: Seconds to wait for model version crreation.
        """
        dst_source = dst_source.replace("file://","") # OSS MLflow
        if not dst_source.startswith("dbfs:") and not dst_source.startswith("s3:") and not os.path.exists(dst_source):
            raise MlflowExportImportException(f"'source' argument for MLflowClient.create_model_version does not exist: {dst_source}", http_status_code=404)
        kwargs = {"await_creation_for": self.await_creation_for } if self.await_creation_for else {}
        tags = src_vr["tags"]
        if self.import_source_tags:
            _set_source_tags_for_field(src_vr, tags)

        dst_vr = self.mlflow_client.create_model_version(
            model_name,
            dst_source, dst_run_id, \
            description=src_vr["description"],
            tags=tags, **kwargs
        )

        model_utils.wait_until_version_is_ready(self.mlflow_client, model_name, dst_vr, sleep_time=sleep_time)
        src_current_stage = src_vr["current_stage"]
        _logger.info(f"Importing model '{model_name}' version {dst_vr.version} stage '{src_current_stage}'")
        if src_current_stage != "None": # fails for Databricks but not OSS
            self.mlflow_client.transition_model_version_stage(model_name, dst_vr.version, src_current_stage)


    def _import_model(self,
            model_name,
            input_dir,
            delete_model = False
        ):
        """
        :param model_name: Model name.
        :param input_dir: Input directory.
        :param delete_model: Delete current model before importing versions.
        :param verbose: Verbose.
        :param sleep_time: Seconds to wait for model version crreation.
        :return: Model import manifest.
        """
        path = os.path.join(input_dir, "model.json")
        model_dct = io_utils.read_file_mlflow(path)["registered_model"]

        _logger.info("Model to import:")
        _logger.info(f"  Name: {model_dct['name']}")
        _logger.info(f"  Description: {model_dct.get('description','')}")
        _logger.info(f"  Tags: {model_dct.get('tags','')}")
        _logger.info(f"  {len(model_dct['versions'])} versions")
        _logger.info(f"  path: {path}")

        if not model_name:
            model_name = model_dct["name"]
        if delete_model:
            model_utils.delete_model(self.mlflow_client, model_name)

        try:
            tags = { e["key"]:e["value"] for e in model_dct.get("tags", {}) }
            if self.import_source_tags:
                _set_source_tags_for_field(model_dct, tags)
            self.mlflow_client.create_registered_model(model_name, tags, model_dct.get("description"))
            _logger.info(f"Created new registered model '{model_name}'")
        except RestException as e:
            if not "RESOURCE_ALREADY_EXISTS: Registered Model" in str(e):
                raise e
            _logger.info(f"Registered model '{model_name}' already exists")

        if self.import_permissions:
            perms_dct = model_dct["permissions"]
            if perms_dct:
                _model = self.dbx_client.get("mlflow/databricks/registered-models/get", { "name": model_name })
                _model2 = _model["registered_model_databricks"]
                model_id = _model2["id"]
                import_permissions(self.dbx_client, perms_dct, "model", model_name, model_id)

        return model_dct


class ModelImporter(BaseModelImporter):
    """ Low-level 'point' model importer.  """

    def __init__(self,
            mlflow_client = None,
            import_permissions = False,
            import_source_tags = False,
            await_creation_for = None
        ):
        super().__init__(
            mlflow_client = mlflow_client,
            import_permissions = import_permissions,
            import_source_tags = import_source_tags,
            await_creation_for = await_creation_for
        )


    def import_model(self,
            model_name,
            input_dir,
            experiment_name,
            delete_model = False,
            verbose = False,
            sleep_time = 30
        ):
        """
        :param model_name: Model name.
        :param input_dir: Input directory.
        :param experiment_name: The name of the experiment.
        :param delete_model: Delete current model before importing versions.
        :param import_source_tags: Import source information for registered model and its versions ad tags in destination object.
        :param verbose: Verbose.
        :param sleep_time: Seconds to wait for model version crreation.
        :return: Model import manifest.
        """
        model_dct = self._import_model(model_name, input_dir, delete_model)
        mlflow.set_experiment(experiment_name)
        _logger.info("Importing versions:")
        for vr in model_dct["versions"]:
            try:
                run_id = self._import_run(input_dir, experiment_name, vr)
                if run_id:
                    self.import_version(model_name, vr, run_id, sleep_time)
            except RestException as e:
                msg = { "model": model_name, "version": vr["version"], "src_run_id": vr["run_id"], "experiment": experiment_name, "RestException": str(e) }
                _logger.error(f"Failed to import model version: {msg}")
        if verbose:
            model_utils.dump_model_versions(self.mlflow_client, model_name)


    def _import_run(self, input_dir, experiment_name, vr):
        run_id = vr["run_id"]
        source = vr["source"]
        current_stage = vr["current_stage"]
        run_artifact_uri = vr.get("_run_artifact_uri",None)
        run_dir = os.path.join(input_dir,run_id)
        if not os.path.exists(run_dir):
            msg = { "model": vr["name"], "version": vr["version"], "experiment": experiment_name, "run_id": run_id }
            _logger.warning(f"Cannot import model version because its run does not exist: {msg}")
            return None
        _logger.info(f"  Version {vr['version']}:")
        _logger.info(f"    current_stage: {current_stage}:")
        _logger.info( "    Source run - run to import:")
        _logger.info(f"      run_id:           {run_id}")
        _logger.info(f"      run_artifact_uri: {run_artifact_uri}")
        _logger.info(f"      source:           {source}")
        model_artifact = _extract_model_path(source, run_id)
        _logger.info(f"      model_artifact:   {model_artifact}")

        dst_run,_ = import_run(
            input_dir = run_dir,
            experiment_name = experiment_name,
            import_source_tags = self.import_source_tags,
            mlflow_client = self.mlflow_client
        )
        dst_run_id = dst_run.info.run_id
        run = self.mlflow_client.get_run(dst_run_id)
        _logger.info( "    Destination run - imported run:")
        _logger.info(f"      run_id: {dst_run_id}")
        _logger.info(f"      run_artifact_uri: {run.info.artifact_uri}")
        source = _path_join(run.info.artifact_uri, model_artifact)
        _logger.info(f"      source:           {source}")
        return dst_run_id


    def import_version(self, model_name, src_vr, dst_run_id, sleep_time):
        dst_run = self.mlflow_client.get_run(dst_run_id)
        model_path = _extract_model_path(src_vr["source"], src_vr["run_id"])
        dst_source = f"{dst_run.info.artifact_uri}/{model_path}"
        self._import_version(model_name, src_vr, dst_run_id, dst_source, sleep_time)


class BulkModelImporter(BaseModelImporter):
    """ Bulk model importer. """

    def __init__(self,
            run_info_map,
            import_permissions = False,
            import_source_tags = False,
            experiment_renames = None,
            await_creation_for = None,
            mlflow_client = None,
        ):
        super().__init__(
            mlflow_client = mlflow_client,
            import_permissions = import_permissions,
            import_source_tags = import_source_tags,
            await_creation_for = await_creation_for
         )
        self.run_info_map = run_info_map
        self.experiment_renames = experiment_renames


    def import_model(self,
            model_name,
            input_dir,
            delete_model = False,
            verbose = False,
            sleep_time = 30
        ):
        """
        :param model_name: Model name.
        :param input_dir: Input directory.
        :param delete_model: Delete current model before importing versions.
        :param verbose: Verbose.
        :param sleep_time: Seconds to wait for model version crreation.
        :return: Model import manifest.
        """
        model_dct = self._import_model(model_name, input_dir, delete_model)
        _logger.info(f"Importing {len(model_dct['versions'])} versions:")
        for vr in model_dct["versions"]:
            src_run_id = vr["run_id"]
            dst_run_info = self.run_info_map.get(src_run_id, None)
            if not dst_run_info:
                msg = { "model": model_name, "version": vr["version"], "stage": vr["current_stage"], "run_id": src_run_id }
                _logger.error(f"Cannot import model version {msg} since the source run_id was probably deleted.")
            else:
                dst_run_id = dst_run_info.run_id
                exp_name = rename_utils.rename(vr["_experiment_name"], self.experiment_renames, "experiment")
                try:
                    mlflow.set_experiment(exp_name)
                    self.import_version(model_name, vr, dst_run_id, sleep_time)
                except RestException as e:
                    msg = { "model": model_name, "version": vr["version"], "experiment": exp_name, "run_id": dst_run_id, "exception": str(e) }
                    _logger.error(f"Failed to import model version: {msg}")
        if verbose:
            model_utils.dump_model_versions(self.mlflow_client, model_name)


    def import_version(self, model_name, src_vr, dst_run_id, sleep_time):
        src_run_id = src_vr["run_id"]
        model_path = _extract_model_path(src_vr["source"], src_run_id) # get path to model artifact
        dst_artifact_uri = self.run_info_map[src_run_id].artifact_uri
        dst_source = f"{dst_artifact_uri}/{model_path}"
        self._import_version(model_name, src_vr, dst_run_id, dst_source, sleep_time)


def _extract_model_path(source, run_id):
    """
    Extract relative path to model artifact from version source field
    :param source: 'source' field of registered model version
    :param run_id: Run ID in the 'source field 
    :return: relative path to the model artifact 
    """
    idx = source.find(run_id)
    if idx == -1:
        raise MlflowExportImportException(f"Cannot find run ID '{run_id}' in registered model version source field '{source}'", http_status_code=404)
    model_path = source[1+idx+len(run_id):]
    pattern = "artifacts"

    idx = source.find(pattern)
    if idx == -1: # Bizarre - sometimes there is no 'artifacts' after run_id
        model_path = ""
    else:
        model_path = source[1+idx+len(pattern):]
    return model_path


def _path_join(x, y):
    """ Account for DOS backslash """
    path = os.path.join(x, y)
    if path.startswith("dbfs:"):
        path = path.replace("\\","/") 
    return path


@click.command()
@opt_input_dir
@opt_model
@opt_experiment_name
@opt_delete_model
@opt_import_permissions
@opt_import_source_tags
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
@opt_verbose

def main(input_dir, model, experiment_name, delete_model, import_permissions, import_source_tags, 
        await_creation_for, sleep_time, verbose
    ):
    _logger.info("Options:")
    for k,v in locals().items():
        _logger.info(f"  {k}: {v}")
    import_model(
        model_name = model,
        experiment_name = experiment_name,
        input_dir = input_dir,
        delete_model = delete_model,
        import_permissions = import_permissions,
        import_source_tags = import_source_tags,
        await_creation_for = await_creation_for,
        sleep_time = sleep_time,
        verbose = verbose
    )


if __name__ == "__main__":
    main()
