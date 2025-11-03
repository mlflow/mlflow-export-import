"""
Exports a logged model to a directory.
"""

import os
import time
import traceback

import click
import mlflow
from mlflow.exceptions import RestException

from mlflow_export_import.client.client_utils import create_mlflow_client
from mlflow_export_import.common import filesystem as _fs
from mlflow_export_import.common import io_utils
from mlflow_export_import.common import utils, logged_model_utils
from mlflow_export_import.common.click_options import (
    opt_model_id,
    opt_output_dir
)
from mlflow_export_import.common.timestamp_utils import format_seconds

_logger = utils.getLogger(__name__)

def export_logged_model(
        model_id,
        output_dir,
        mlflow_client = None
    ):
    """
    :param model_id: Logged model ID
    :param output_dir: Output directory
    :param mlflow_client: MLflow client
    """

    mlflow_client = mlflow_client or create_mlflow_client()
    start_time = time.time()
    logged_model = None
    try:
        logged_model = mlflow_client.get_logged_model(model_id)
        artifacts = mlflow.artifacts.list_artifacts(logged_model.artifact_location)
        fs = _fs.get_filesystem(".")

        mlflow_attr = logged_model_utils.logged_model_to_json(logged_model)

        if logged_model.source_run_id:
            run = mlflow_client.get_run(logged_model.source_run_id)
            mlflow_attr["dataset_inputs"] = _inputs_to_dict(run.inputs)

        io_utils.write_export_file(output_dir, "logged_model.json", __file__, mlflow_attr)

        if len(artifacts) > 0:
            fs.mkdirs(output_dir)
            mlflow.artifacts.download_artifacts(
                artifact_uri=logged_model.artifact_location,
                dst_path=_fs.mk_local_path(output_dir),
                tracking_uri=mlflow_client._tracking_client.tracking_uri)

        msg = {"model_id": model_id, "name": logged_model.name, "experiment_id": logged_model.experiment_id}
        dur = format_seconds(time.time() - start_time)
        _logger.info(f"Exported logged model in {dur}: {msg}")
        return logged_model
    except RestException as e:
        err_msg = {"model_id": model_id, "experiment_id": logged_model.experiment_id, "RestException": e.json}
        _logger.error(f"Logged model export failed (1): {err_msg}")
        return None
    except Exception as e:
        err_msg = {"model_id": model_id, "experiment_id": logged_model.experiment_id, "Exception": e}
        _logger.error(f"Logged model export failed (2): {err_msg}")
        traceback.print_exc()
        return None

def _inputs_to_dict(inputs):
    def to_dict(ds):
        return {
            "dataset": utils.strip_underscores(ds.dataset),
            "tags": [ utils.strip_underscores(tag) for tag in ds.tags ]
        }
    return [ to_dict(x) for x in inputs.dataset_inputs ]

@click.command()
@opt_model_id
@opt_output_dir
def main(model_id, output_dir):
    _logger.info("Options:")
    for k, v in locals().items():
        _logger.info(f"  {k}: {v}")

    export_logged_model(model_id, output_dir)


if __name__ == "__main__":
    main()