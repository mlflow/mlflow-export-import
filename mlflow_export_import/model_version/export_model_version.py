"""
Exports a registered model version and its run.
"""

import os
import time
import click

from mlflow_export_import.client.client_utils import create_mlflow_client, create_http_client
from mlflow_export_import.common import utils, io_utils, model_utils
from mlflow_export_import.common.timestamp_utils import adjust_timestamps, format_seconds
from mlflow_export_import.run.export_run import export_run
from mlflow_export_import.common.click_options import (
    opt_model,
    opt_output_dir,
    opt_export_permissions,
    opt_notebook_formats
)
from . click_options import (
    opt_version,
    opt_vrm_export_version_model,
    opt_vrm_model_artifact_path,
    opt_skip_download_run_artifacts
)

_logger = utils.getLogger(__name__)

VERSION_MODEL_ARTIFACT_PATH = "version_model"


def export_model_version(
        model_name,
        version,
        output_dir,
        export_version_model = False,
        vrm_model_artifact_path = "",
        skip_download_run_artifacts = False,
        export_permissions = False,
        notebook_formats = None,
        mlflow_client = None
    ):
    """
    Exports a model version.

    :param model_name: Registered model name.
    :param version: Registered model version.
    :param output_dir: Export directory.
    :param export_version_model: Export model version's 'cached" MLflow model clone.
    :param export_version_model: Export model version's MLflow model.
    :param vrm_model_artifact_path:
    :param skip_download_run_artifacts: Don't download the run's artifacts.
    :param export_permissions: Export Databricks permissions.
    :param notebook_formats: List of Databricks notebook formats. Values are SOURCE, HTML, JUPYTER or DBC (comma separated)
    :param mlflow_client: MlflowClient (optional).

    :return: Returns model version object.
    """
    mlflow_client = mlflow_client or create_mlflow_client()

    _model = mlflow_client.get_registered_model(model_name)
    vr = mlflow_client.get_model_version(model_name, version)
    vr_dct = model_utils.model_version_to_dict(vr)

    _export_registered_model(mlflow_client, model_name, export_permissions, output_dir)

    run = export_run(
        run_id = vr.run_id,
        output_dir = os.path.join(output_dir, "run"),
        notebook_formats = notebook_formats,
        export_deleted_runs = True, # NOTE: Important since default is not export a deleted run
        skip_download_run_artifacts = skip_download_run_artifacts,
        mlflow_client = mlflow_client
    )
    if not run:
        msg = f"Cannot get run ID '{vr.run_id}' of model version '{model_name}/{version}'"
        _logger.error(f"{msg}")
    else:
        _export_experiment(mlflow_client, run.info.experiment_id, output_dir)

    info_attr = {}
    if export_version_model:
        _export_version_model(mlflow_client, output_dir, vr, vr_dct, info_attr, export_version_model, vrm_model_artifact_path)

    adjust_timestamps(vr_dct, ["creation_timestamp", "last_updated_timestamp"])
    mlflow_attr = { "model_version": vr_dct}
    msg = utils.get_obj_key_values(vr, [ "name", "version", "alias", "current_stage", "status", "run_id" ])
    _logger.info(f"Exporting model verson: {msg}")

    io_utils.write_export_file(output_dir, "version.json", __file__, mlflow_attr, info_attr)
    return vr

def _export_version_model(mlflow_client,
        output_dir, vr,
        vr_dct,
        info_attr,
        export_version_model,
        vrm_model_artifact_path
    ):
    start_time = time.time()
    if vrm_model_artifact_path:
        _output_dir = os.path.join(output_dir, f"run/artifacts/{vrm_model_artifact_path}")
        vr_dct["source"] = vrm_model_artifact_path
        vr_dct["_source"] = vr.source
    else:
        _output_dir = os.path.join(output_dir, VERSION_MODEL_ARTIFACT_PATH)
    vr_dct["_download_uri"] = model_utils.export_version_model(mlflow_client, vr, _output_dir)
    info_attr["vrm_export_version_model"] = export_version_model
    info_attr["vrm_model_artifact_path"] = vrm_model_artifact_path
    info_attr["vrm_model_artifact_full_path"] = _output_dir

    dur = format_seconds(time.time()-start_time)
    msg = { "model": f'{vr_dct["name"]}/{vr_dct["version"]}', "output_dir": _output_dir }
    _logger.info(f"Exported registry MLflow model in {dur}: {msg}")


def _export_experiment(mlflow_client, experiment_id, output_dir):
    http_client = create_http_client(mlflow_client)
    exp = http_client.get("experiments/get", {"experiment_id": experiment_id})
    exp = exp["experiment"]
    msg = { "name": exp["name"], "experiment_id": exp["experiment_id"] }
    _logger.info(f"Exporting experiment: {msg}")

    adjust_timestamps(exp, ["creation_time", "last_update_time"])
    mlflow_attr = { "experiment": exp }
    io_utils.write_export_file(output_dir, "experiment.json", __file__, mlflow_attr, {})


def _export_registered_model(mlflow_client, model_name, export_permissions, output_dir):
    model = model_utils.get_registered_model(mlflow_client, model_name, export_permissions)
    msg = {"name": model["name"] }
    _logger.info(f"Exporting registered model: {msg}")
    adjust_timestamps(model, ["creation_timestamp", "last_updated_timestamp"])
    mlflow_attr = { "registered_model": model }
    io_utils.write_export_file(output_dir, "model.json", __file__, mlflow_attr, {})


@click.command()
@opt_model
@opt_version
@opt_output_dir
@opt_vrm_export_version_model
@opt_vrm_model_artifact_path
@opt_skip_download_run_artifacts
@opt_export_permissions
@opt_notebook_formats

def main(model,
        version,
        output_dir,
        vrm_export_version_model,
        vrm_model_artifact_path,
        skip_download_run_artifacts,
        export_permissions,
        notebook_formats,
    ):
    """
    Exports a registered model version and its run.
    """
    _logger.info("Options:")
    for k,v in locals().items():
        _logger.info(f"  {k}: {v}")
    export_model_version(
        model_name = model,
        version = version,
        output_dir = output_dir,
        export_version_model = vrm_export_version_model,
        vrm_model_artifact_path = vrm_model_artifact_path,
        skip_download_run_artifacts = skip_download_run_artifacts,
        export_permissions = export_permissions,
        notebook_formats = notebook_formats
    )


if __name__ == "__main__":
    main()
