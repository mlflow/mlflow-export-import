"""
Exports a registered model version and its run.
"""

import os
import click
import mlflow

from mlflow_export_import.common import model_utils
from mlflow_export_import.common.click_options import (
    opt_model,
    opt_output_dir,
    opt_notebook_formats,
    opt_export_version_model
)
from . click_options import (
    opt_version,
)

from mlflow_export_import.common import utils, io_utils
from mlflow_export_import.common.timestamp_utils import fmt_ts_millis
from mlflow_export_import.run.export_run import export_run

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
    :param model_name: Registered model name.
    :param model_name: Registered model version.
    :param output_dir: Export directory.
    :param notebook_formats: List of notebook formats to export. Values are SOURCE, HTML, JUPYTER or DBC.
    :param mlflow_client: MlflowClient
    :return: Returns model version
    """

    mlflow_client = mlflow_client or mlflow.MlflowClient()

    vr = mlflow_client.get_model_version(model_name, version)

    export_run(
        run_id = vr.run_id,
        output_dir = os.path.join(output_dir, "run"),
        notebook_formats = notebook_formats,
        export_deleted_runs = True, # NOTE: Important since default is not export a deleted run
        mlflow_client = mlflow_client
    )

    vr_dict = dict(vr)
    if export_version_model:
        _output_dir = os.path.join(output_dir, "mlflow_model")
        vr_dict["_download_uri"] = model_utils.export_version_model(mlflow_client, vr, _output_dir)

    info_attr = {}
    mlflow_attr = { "model_version": _adjust_version(vr_dict) }
    msg = utils.get_obj_key_values(vr, [ "name", "version", "current_stage", "status", "run_id" ])
    _logger.info(f"Exporting model verson: {msg}")

    io_utils.write_export_file(output_dir, "model_version.json", __file__, mlflow_attr, info_attr)
    return vr


def _adjust_version(vr):
    """
    Add nicely formatted timestamps and for aesthetic reasons order the dict attributes
    """
    def _adjust_timestamp(dct, attr):
        dct[f"_{attr}"] = fmt_ts_millis(dct.get(attr))
    _adjust_timestamp(vr, "creation_timestamp")
    _adjust_timestamp(vr, "last_updated_timestamp")
    return vr


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
