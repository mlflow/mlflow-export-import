"""
Exports a registered model version and its run.
"""

import os
import click
import mlflow

from mlflow_export_import.client.http_client import create_http_client
from mlflow_export_import.common import utils, io_utils, model_utils
from mlflow_export_import.common.timestamp_utils import fmt_ts_millis
from mlflow_export_import.run.export_run import export_run
from mlflow_export_import.common.click_options import (
    opt_model,
    opt_output_dir,
    opt_notebook_formats,
    opt_export_version_model
)
from . click_options import opt_version

_logger = utils.getLogger(__name__)


def export_model_version(
        model_name,
        version,
        output_dir,
        export_version_model = False,
        notebook_formats = None,
        mlflow_client = None
    ):
    """
    Exports model version.

    :param model_name: Registered model name.
    :param version: Registered model version.
    :param output_dir: Export directory.
    :param export_version_model: Export model version's 'cached" MLflow model clone..
    :param notebook_formats: List of Databricks notebook formats. Values are SOURCE, HTML, JUPYTER or DBC (comma separated)
    :param mlflow_client: MlflowClient (optional).

    :return: Returns model version object.
    """

    mlflow_client = mlflow_client or mlflow.MlflowClient()

    _model = mlflow_client.get_registered_model(model_name)
    vr = mlflow_client.get_model_version(model_name, version)
    vr_dct = model_utils.model_version_to_dict(vr)

    run = export_run(
        run_id = vr.run_id,
        output_dir = os.path.join(output_dir, "run"),
        notebook_formats = notebook_formats,
        export_deleted_runs = True, # NOTE: Important since default is not export a deleted run
        mlflow_client = mlflow_client
    )
    info_attr = {}
    if export_version_model:
        _output_dir = os.path.join(output_dir, "mlflow_model")
        vr_dct["_download_uri"] = model_utils.export_version_model(mlflow_client, vr, _output_dir)
        info_attr["export_version_model"] = True

    export_experiment(mlflow_client, run.info.experiment_id, output_dir)
    _export_model(mlflow_client, model_name, output_dir)

    _adjust_timestamp(vr_dct, "creation_timestamp")
    _adjust_timestamp(vr_dct, "last_updated_timestamp")
    mlflow_attr = { "model_version": vr_dct}
    msg = utils.get_obj_key_values(vr, [ "name", "version", "current_stage", "status", "run_id" ])
    _logger.info(f"Exporting model verson: {msg}")

    io_utils.write_export_file(output_dir, "model_version.json", __file__, mlflow_attr, info_attr)
    return vr


def export_experiment(mlflow_client, experiment_id, output_dir):
    http_client = create_http_client(mlflow_client)
    exp = http_client.get("experiments/get", {"experiment_id": experiment_id})
    exp = exp["experiment"]
    msg = { "name": exp["name"], "experiment_id": exp["experiment_id"] }
    _logger.info(f"Exporting experiment: {msg}")

    _adjust_timestamp(exp, "creation_time")
    _adjust_timestamp(exp, "last_update_time")
    mlflow_attr = { "experiment": exp }
    io_utils.write_export_file(output_dir, "experiment.json", __file__, mlflow_attr, {})


def _export_model(mlflow_client, model_name, output_dir):
    http_client = create_http_client(mlflow_client, model_name)
    model = http_client.get("registered-models/get", {"name": model_name})
    model = model.pop("registered_model")
    model.pop("latest_versions", None)
    msg = {"name": model["name"] }
    _logger.info(f"Exporting registered model: {msg}")

    _adjust_timestamp(model, "creation_timestamp")
    _adjust_timestamp(model, "last_updated_timestamp")

    mlflow_attr = { "model": model }
    io_utils.write_export_file(output_dir, "registered_model.json", __file__, mlflow_attr, {})


def _adjust_version(vr):
    """
    Add nicely formatted timestamps and for aesthetic reasons order the dict attributes
    """
    _adjust_timestamp(vr, "creation_timestamp")
    _adjust_timestamp(vr, "last_updated_timestamp")
    return vr


def _adjust_timestamp(dct, key):
    if key in dct:
        dct[f"_{key}"] = fmt_ts_millis(dct.get(key))


@click.command()
@opt_model
@opt_version
@opt_output_dir
@opt_export_version_model
@opt_notebook_formats
def main(model,
        version,
        output_dir,
        export_version_model,
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
        export_version_model = export_version_model,
        notebook_formats = notebook_formats
    )


if __name__ == "__main__":
    main()
