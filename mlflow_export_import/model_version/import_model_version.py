"""
Imports a registered model version and its run.
Optionally import registered model and experiment metadata.
"""

import os
import time
import click

from mlflow_export_import.common.click_options import (
    opt_input_dir,
    opt_model,
    opt_import_permissions,
    opt_import_source_tags
)
from . click_options import (
    opt_create_model,
    opt_experiment_name,
    opt_import_metadata,
    opt_import_stages_and_aliases
)
from mlflow_export_import.common import MlflowExportImportException
from mlflow_export_import.common import utils, io_utils, mlflow_utils, model_utils
from mlflow_export_import.common.mlflow_utils import MlflowTrackingUriTweak
from mlflow_export_import.common.source_tags import set_source_tags_for_field, fmt_timestamps
from mlflow_export_import.common.timestamp_utils import format_seconds
from mlflow_export_import.run.import_run import import_run
from mlflow_export_import.client.client_utils import create_mlflow_client, create_dbx_client

_logger = utils.getLogger(__name__)


def import_model_version(
        model_name,
        experiment_name,
        input_dir,
        create_model = False,
        import_permissions = False,
        import_source_tags = False,
        import_stages_and_aliases = True,
        import_metadata = False,
        mlflow_client = None
    ):
    """
    Exports a model version.

    :param model_name: Registered model name.
    :param experiment_name: Destination experiment name for the version's run.
    :param input_dir: Import directory.
    :param create_model: Create registered model before creating model version.
    :param import_source_tags: Import source information for registered model and its versions and tags in destination object.
    :param import_stages_and_aliases: Import stages and aliases.
    :param import_metadata: Import registered model and experiment metadata.
    :param mlflow_client: MlflowClient (optional).

    :return: Returns model version object.
    """

    mlflow_client = mlflow_client or create_mlflow_client()

    path = os.path.join(input_dir, "version.json")
    src_vr = io_utils.read_file_mlflow(path)["model_version"]

    dbx_client = create_dbx_client(mlflow_client)
    if import_metadata:
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
        path = os.path.join(input_dir, "model.json")
        model_dct = io_utils.read_file_mlflow(path)["registered_model"]
        created_model = model_utils.create_model(mlflow_client, model_name, model_dct, import_metadata)
        perms = model_dct.get("permissions")
        if created_model and import_permissions and perms:
            model_utils.update_model_permissions(mlflow_client, dbx_client, model_name, perms)

    model_path = _get_model_path(src_vr)
    dst_source = f"{dst_run.info.artifact_uri}/{model_path}"
    dst_vr = _import_model_version(
        mlflow_client,
        model_name = model_name,
        src_vr = src_vr,
        dst_run_id = dst_run.info.run_id,
        dst_source = dst_source,
        import_stages_and_aliases = import_stages_and_aliases,
        import_source_tags = import_source_tags
    )
    return dst_vr

def _import_model_version(
        mlflow_client,
        model_name,
        src_vr,
        dst_run_id,
        dst_source,
        import_stages_and_aliases = True,
        import_source_tags = False
    ):
    start_time = time.time()
    dst_source = dst_source.replace("file://","") # OSS MLflow
    if not dst_source.startswith("dbfs:") and not os.path.exists(dst_source):
        raise MlflowExportImportException(f"'source' argument for MLflowClient.create_model_version does not exist: {dst_source}", http_status_code=404)

    tags = src_vr["tags"]
    if import_source_tags:
        _set_source_tags_for_field(src_vr, tags)

    # NOTE: MLflow UC bug:
    # The client's tracking_uri is not honored. Instead MlflowClient.create_model_version()
    # seems to use mlflow.tracking_uri internally to download run artifacts for UC models.
    _logger.info(f"Importing model version '{model_name}'")
    with MlflowTrackingUriTweak(mlflow_client):
        dst_vr = mlflow_client.create_model_version(
            name = model_name,
            source = dst_source,
            run_id = dst_run_id,
            description = src_vr.get("description"),
            tags = tags
        )

    if import_stages_and_aliases:
        for alias in src_vr.get("aliases",[]):
            mlflow_client.set_registered_model_alias(dst_vr.name, alias, dst_vr.version)

        if not model_utils.is_unity_catalog_model(model_name):
            src_current_stage = src_vr["current_stage"]
            if src_current_stage and src_current_stage != "None": # fails for Databricks  but not OSS
                mlflow_client.transition_model_version_stage(model_name, dst_vr.version, src_current_stage)

    dur = format_seconds(time.time()-start_time)
    _logger.info(f"Imported model version '{model_name}/{dst_vr.version}' in {dur}")
    return mlflow_client.get_model_version(dst_vr.name, dst_vr.version)


def _get_model_path(src_vr):
    source = src_vr["source"]
    model_path = _extract_model_path(source)
    if not model_path:
        model_path = os.path.basename(source)
    return model_path


def _extract_model_path(source):
    """
    Extract relative path to model artifact from version source field
    :param source: 'source' field of registered model version
    :return: relative path to the model artifact
    """
    pattern = "artifacts"
    idx = source.find(pattern)
    if idx == -1:
        return None
    return source[1+idx+len(pattern):]


def _set_source_tags_for_field(dct, tags):
    set_source_tags_for_field(dct, tags)
    fmt_timestamps("creation_timestamp", dct, tags)
    fmt_timestamps("last_updated_timestamp", dct, tags)


@click.command()
@opt_model
@opt_experiment_name
@opt_input_dir
@opt_create_model
@opt_import_permissions
@opt_import_source_tags
@opt_import_stages_and_aliases
@opt_import_metadata

def main(input_dir, model, experiment_name, create_model, import_permissions, import_source_tags, import_stages_and_aliases, import_metadata):
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
        import_permissions = import_permissions,
        import_source_tags = import_source_tags,
        import_stages_and_aliases = import_stages_and_aliases,
        import_metadata = import_metadata
    )


if __name__ == "__main__":
    main()
