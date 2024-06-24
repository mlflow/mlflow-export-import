"""
Exports a run to a directory.
"""

import os
import time
import traceback
import click
import mlflow

from mlflow_export_import.common import utils
from mlflow_export_import.common.click_options import (
    opt_run_id,
    opt_output_dir,
    opt_notebook_formats
)
from mlflow.exceptions import RestException
from mlflow_export_import.common import filesystem as _fs
from mlflow_export_import.common import io_utils
from mlflow_export_import.common.timestamp_utils import adjust_timestamps, format_seconds
from mlflow_export_import.client.client_utils import create_mlflow_client, create_dbx_client
from mlflow_export_import.notebook.download_notebook import download_notebook

from mlflow.utils.mlflow_tags import MLFLOW_DATABRICKS_NOTEBOOK_PATH
MLFLOW_DATABRICKS_NOTEBOOK_REVISION_ID = "mlflow.databricks.notebookRevisionID" # NOTE: not in mlflow/utils/mlflow_tags.py

_logger = utils.getLogger(__name__)


def export_run(
        run_id,
        output_dir,
        export_deleted_runs = False,
        skip_download_run_artifacts = False,
        notebook_formats = None,
        raise_exception = False,
        mlflow_client = None
    ):
    """
    :param run_id: Run ID.
    :param output_dir: Output directory.
    :param export_deleted_runs: Export deleted runs.
    :param notebook_formats: List of notebook formats to export. Values are SOURCE, HTML, JUPYTER or DBC.
    :param raise_exception: Raise an exception instead of just logging error and returning None.
    :param mlflow_client: MLflow client.
    :return: Run or None if the run was not exported due to export_deleted_runs or errors.
    """

    mlflow_client = mlflow_client or create_mlflow_client()
    dbx_client = create_dbx_client(mlflow_client)

    if notebook_formats is None:
        notebook_formats = []

    start_time = time.time()
    experiment_id = None
    try:
        run = mlflow_client.get_run(run_id)
        dst_path = os.path.join(output_dir, "artifacts")
        msg = { "run_id": run.info.run_id, "dst_path": dst_path }
        if run.info.lifecycle_stage == "deleted" and not export_deleted_runs:
            _logger.warning(f"Not exporting run '{run.info.run_id} because its lifecycle_stage is '{run.info.lifecycle_stage}'")
            return None
        experiment_id = run.info.experiment_id
        msg = { "run_id": run.info.run_id, "lifecycle_stage": run.info.lifecycle_stage, "experiment_id": run.info.experiment_id }
        tags = run.data.tags
        tags = dict(sorted(tags.items()))

        info = utils.strip_underscores(run.info)
        adjust_timestamps(info, ["start_time", "end_time"])
        mlflow_attr = {
            "info": info,
            "params": run.data.params,
            "metrics": _get_metrics_with_steps(mlflow_client, run),
            "tags": tags,
            "inputs": _inputs_to_dict(run.inputs)
        }
        io_utils.write_export_file(output_dir, "run.json", __file__, mlflow_attr)
        fs = _fs.get_filesystem(".")

        # copy artifacts
        _logger.info(f"Exporting run: {msg}")
        artifacts = mlflow_client.list_artifacts(run.info.run_id)

        if skip_download_run_artifacts:
            _logger.warning(f"Not downloading run artifacts for run {run.info.run_id}")
        else:
            if len(artifacts) > 0: # Because of https://github.com/mlflow/mlflow/issues/2839
                fs.mkdirs(dst_path)
                mlflow.artifacts.download_artifacts(
                    run_id = run.info.run_id,
                    dst_path = _fs.mk_local_path(dst_path),
                    tracking_uri = mlflow_client._tracking_client.tracking_uri)
        notebook = tags.get(MLFLOW_DATABRICKS_NOTEBOOK_PATH)

        # export notebook as artifact
        if notebook is not None:
            if len(notebook_formats) > 0:
                _export_notebook(dbx_client, output_dir, notebook, notebook_formats, run, fs)
        elif len(notebook_formats) > 0:
            _logger.warning(f"No notebooks to export for run '{run_id}' since tag '{MLFLOW_DATABRICKS_NOTEBOOK_PATH}' is not set.")
        dur = format_seconds(time.time()-start_time)
        _logger.info(f"Exported run in {dur}: {msg}")
        return run

    except RestException as e:
        if raise_exception:
            raise e
        err_msg = { "run_id": run_id, "experiment_id": experiment_id, "RestException": e.json }
        _logger.error(f"Run export failed (1): {err_msg}")
        return None
    except Exception as e:
        if raise_exception:
            raise e
        err_msg = { "run_id": run_id, "experiment_id": experiment_id, "Exception": e }
        _logger.error(f"Run export failed (2): {err_msg}")
        traceback.print_exc()
        return None


def _get_metrics_with_steps(mlflow_client, run):
    metrics_with_steps = {}
    for metric in run.data.metrics.keys():
        metric_history = mlflow_client.get_metric_history(run.info.run_id,metric)
        lst = [utils.strip_underscores(m) for m in metric_history]
        for x in lst:
            del x["key"]
        metrics_with_steps[metric] = lst
    return metrics_with_steps


def _export_notebook(dbx_client, output_dir, notebook, notebook_formats, run, fs):
    notebook_dir = os.path.join(output_dir, "artifacts", "notebooks")
    fs.mkdirs(notebook_dir)
    revision_id = run.data.tags.get(MLFLOW_DATABRICKS_NOTEBOOK_REVISION_ID)
    if not revision_id:
        _logger.warning(f"Cannot download notebook '{notebook}' for run '{run.info.run_id}' since tag '{MLFLOW_DATABRICKS_NOTEBOOK_REVISION_ID}' does not exist. Notebook is probably a Git Repo notebook.")
        return
    manifest = {
       MLFLOW_DATABRICKS_NOTEBOOK_PATH: run.data.tags[MLFLOW_DATABRICKS_NOTEBOOK_PATH],
       MLFLOW_DATABRICKS_NOTEBOOK_REVISION_ID: revision_id,
       "formats": notebook_formats
    }
    path = os.path.join(notebook_dir, "manifest.json")
    io_utils.write_file(path, manifest)
    download_notebook(notebook_dir, notebook, revision_id, notebook_formats, dbx_client)


def _inputs_to_dict(inputs):
    def to_dict(ds):
        return {
            "dataset": utils.strip_underscores(ds.dataset),
            "tags": [ utils.strip_underscores(tag) for tag in ds.tags ]
        }
    return [ to_dict(x) for x in inputs.dataset_inputs ]


@click.command()
@opt_run_id
@opt_output_dir
@opt_notebook_formats

def main(run_id, output_dir, notebook_formats):
    _logger.info("Options:")
    for k,v in locals().items():
        _logger.info(f"  {k}: {v}")
    export_run(
        run_id = run_id,
        output_dir = output_dir,
        notebook_formats = utils.string_to_list(notebook_formats)
    )


if __name__ == "__main__":
    main()
