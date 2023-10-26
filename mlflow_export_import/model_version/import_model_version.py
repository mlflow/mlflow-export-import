"""
Imports a registered model version and its run.
Optionally import registered model and experiment metadata.
"""

import os
import click
import mlflow

from mlflow_export_import.common.click_options import (
    opt_input_dir,
    opt_model,
    opt_import_source_tags
)
from . click_options import (
    opt_create_model,
    opt_experiment_name,
    opt_import_metadata
)
from mlflow_export_import.common import MlflowExportImportException
from mlflow_export_import.common import utils, io_utils, mlflow_utils, model_utils
from mlflow_export_import.common.mlflow_utils import MlflowTrackingUriTweak
from mlflow_export_import.common.source_tags import set_source_tags_for_field, fmt_timestamps
from mlflow_export_import.run.import_run import import_run
from mlflow_export_import.client.http_client import create_dbx_client

_logger = utils.getLogger(__name__)


def import_model_version(
        model_name,
        experiment_name,
        input_dir,
        create_model = False,
        import_source_tags = False,
        import_metadata = False,
        await_creation_for = None,
        mlflow_client = None
    ):
    mlflow_client = mlflow_client or mlflow.MlflowClient()

    path = os.path.join(input_dir, "model_version.json")
    src_vr = io_utils.read_file_mlflow(path)["model_version"]

    if import_metadata:
        dbx_client = create_dbx_client(mlflow_client)
        path = os.path.join(input_dir, "experiment.json")
        exp = io_utils.read_file_mlflow(path)["experiment"]
        tags = utils.mk_tags_dict(exp.get("tags"))
        mlflow_utils.set_experiment(mlflow_client, dbx_client, experiment_name, tags)

    path = os.path.join(input_dir, "run")
    dst_run, _ = import_run(
        input_dir = path,
        experiment_name = experiment_name,
        import_source_tags = import_source_tags,
        mlflow_client = mlflow_client
    )

    if create_model:
        path = os.path.join(input_dir, "registered_model.json")
        mm = io_utils.read_file_mlflow(path)["model"]
        if import_metadata:
            tags = utils.mk_tags_dict(mm.get("tags"))
            model_utils.create_model(mlflow_client, model_name, tags, mm.get("description"))
        else:
            model_utils.create_model(mlflow_client, model_name)

    model_path = _extract_model_path(src_vr["source"], src_vr["run_id"])
    dst_source = f"{dst_run.info.artifact_uri}/{model_path}"
    dst_vr = _import_model_version(
        mlflow_client,
        model_name = model_name,
        src_vr = src_vr,
        dst_run_id = dst_run.info.run_id,
        dst_source = dst_source,
        await_creation_for = await_creation_for
    )
    return dst_vr


def _import_model_version(
        mlflow_client,
        model_name,
        src_vr,
        dst_run_id,
        dst_source,
        import_source_tags = False,
        await_creation_for = None
    ):
    dst_source = dst_source.replace("file://","") # OSS MLflow
    if not dst_source.startswith("dbfs:") and not os.path.exists(dst_source):
        raise MlflowExportImportException(f"'source' argument for MLflowClient.create_model_version does not exist: {dst_source}", http_status_code=404)
    tags = src_vr["tags"]
    if import_source_tags:
        _set_source_tags_for_field(src_vr, tags)

    # NOTE: MLflow UC bug:
    # The client's tracking_uri is not honored. Instead MlflowClient.create_model_version()
    # seems to use mlflow.tracking_uri internally to download run artifacts for UC models.
    with MlflowTrackingUriTweak(mlflow_client):
        kwargs = {"await_creation_for": await_creation_for } if await_creation_for else {}
        dst_vr = mlflow_client.create_model_version(
            name = model_name,
            source = dst_source,
            run_id = dst_run_id,
            description = src_vr.get("description"),
            tags = tags,
            **kwargs
        )
    msg = utils.get_obj_key_values(dst_vr, [ "name", "version", "current_stage", "status" ])
    _logger.info(f"Importing model version: {msg}")

    for alias in src_vr.get("aliases",[]):
        mlflow_client.set_registered_model_alias(dst_vr.name, alias, dst_vr.version)

    if not model_utils.is_unity_catalog_model(model_name):
        src_current_stage = src_vr["current_stage"]
        if src_current_stage and src_current_stage != "None": # fails for Databricks  but not OSS
            mlflow_client.transition_model_version_stage(model_name, dst_vr.version, src_current_stage)

    return mlflow_client.get_model_version(dst_vr.name, dst_vr.version)


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


def _set_source_tags_for_field(dct, tags):
    set_source_tags_for_field(dct, tags)
    fmt_timestamps("creation_timestamp", dct, tags)
    fmt_timestamps("last_updated_timestamp", dct, tags)


@click.command()
@opt_input_dir
@opt_model
@opt_create_model
@opt_experiment_name
@opt_import_source_tags
@opt_import_metadata

def main(input_dir, model, experiment_name, create_model, import_source_tags, import_metadata):
    """
    Imports a registered model version and its run.
    """
    _logger.info("Options:")
    for k,v in locals().items():
        _logger.info(f"  {k}: {v}")
    import_model_version(
        model_name = model,
        experiment_name = experiment_name,
        input_dir = input_dir,
        create_model = create_model,
        import_source_tags = import_source_tags,
        import_metadata = import_metadata
    )


if __name__ == "__main__":
    main()
