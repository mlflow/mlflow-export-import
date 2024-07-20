"""
Exports an experiment to a directory.
"""

import os
import click

from mlflow_export_import.common.click_options import (
    opt_experiment,
    opt_output_dir,
    opt_run_ids,
    opt_notebook_formats,
    opt_export_permissions,
    opt_run_start_time,
    opt_export_deleted_runs,
    opt_check_nested_runs
)
from mlflow_export_import.common.iterators import SearchRunsIterator
from mlflow_export_import.common import utils, io_utils, mlflow_utils
from mlflow_export_import.common import ws_permissions_utils
from mlflow_export_import.common.timestamp_utils import fmt_ts_millis, utc_str_to_millis
from mlflow_export_import.client.client_utils import create_mlflow_client, create_dbx_client
from mlflow_export_import.run.export_run import export_run
from . import nested_runs_utils

_logger = utils.getLogger(__name__)


def export_experiment(
        experiment_id_or_name,
        output_dir,
        run_ids = None,
        export_permissions = False,
        run_start_time = None,
        export_deleted_runs = False,
        check_nested_runs = False,
        notebook_formats = None,
        mlflow_client = None
    ):
    """
    :param: experiment_id_or_name: Experiment ID or name.
    :param: output_dir: Output directory.
    :param: run_ids: List of run IDs to export. If None then export all run IDs.
    :param: export_permissions - Export Databricks permissions.
    :param: export_deleted_runs - Export deleted runs.
    :param: check_nested_runs - Check if run in the 'run-ids' option is a parent of nested runs and 
        export all the nested runs.
    :param: run_start_time - Only export runs started after this UTC time (inclusive). Format: YYYY-MM-DD.
    :param: notebook_formats: List of notebook formats to export. Values are SOURCE, HTML, JUPYTER or DBC.
    :param: mlflow_client: MLflow client.
    :return: Number of successful and number of failed runs.
    """
    mlflow_client = mlflow_client or create_mlflow_client()
    dbx_client = create_dbx_client(mlflow_client)

    run_start_time_str = run_start_time
    if run_start_time:
        run_start_time = utc_str_to_millis(run_start_time)

    exp = mlflow_utils.get_experiment(mlflow_client, experiment_id_or_name)
    msg = { "name": exp.name, "id": exp.experiment_id,
        "mlflow.experimentType": exp.tags.get("mlflow.experimentType", None),
        "lifecycle_stage": exp.lifecycle_stage
    }
    _logger.info(f"Exporting experiment: {msg}")
    ok_run_ids = []
    failed_run_ids = []
    num_runs_exported = 0
    if run_ids:
        runs = _get_runs(mlflow_client, run_ids, exp, failed_run_ids)
        if check_nested_runs: # ZZ
            runs = nested_runs_utils.get_nested_runs(mlflow_client, runs) # 
    else:
        kwargs = {}
        if run_start_time:
            kwargs["filter"] = f"start_time > {run_start_time}"
        if export_deleted_runs:
            from mlflow.entities import ViewType
            kwargs["view_type"] = ViewType.ALL
        runs = SearchRunsIterator(mlflow_client, exp.experiment_id, **kwargs)

    for run in runs:
        _export_run(mlflow_client, run, output_dir, ok_run_ids, failed_run_ids,
            run_start_time, run_start_time_str, export_deleted_runs, notebook_formats)
        num_runs_exported += 1

    info_attr = {
        "num_total_runs": (num_runs_exported),
        "num_ok_runs": len(ok_run_ids),
        "num_failed_runs": len(failed_run_ids),
        "failed_runs": failed_run_ids
    }
    exp_dct = utils.strip_underscores(exp)
    exp_dct["_creation_time"] = fmt_ts_millis(exp.creation_time)
    exp_dct["_last_update_time"] = fmt_ts_millis(exp.last_update_time)
    exp_dct["tags"] = dict(sorted(exp_dct["tags"].items()))

    mlflow_attr = { "experiment": exp_dct , "runs": ok_run_ids }
    if export_permissions:
        mlflow_attr["permissions"] = ws_permissions_utils.get_experiment_permissions(dbx_client, exp.experiment_id)
    io_utils.write_export_file(output_dir, "experiment.json", __file__, mlflow_attr, info_attr)

    msg = f"for experiment '{exp.name}' (ID: {exp.experiment_id})"
    if num_runs_exported==0:
        _logger.warning(f"No runs exported {msg}")
    elif len(failed_run_ids) == 0:
        _logger.info(f"{len(ok_run_ids)} runs succesfully exported {msg}")
    else:
        _logger.info(f"{len(ok_run_ids)}/{num_runs_exported} runs succesfully exported {msg}")
        _logger.info(f"{len(failed_run_ids)}/{num_runs_exported} runs failed {msg}")
    return len(ok_run_ids), len(failed_run_ids)


def _export_run(mlflow_client, run, output_dir,
        ok_run_ids, failed_run_ids,
        run_start_time, run_start_time_str,
        export_deleted_runs, notebook_formats
    ):
    if run_start_time and run.info.start_time < run_start_time:
        msg = {
            "run_id": {run.info.run_id},
            "experiment_id": {run.info.experiment_id},
            "start_time": fmt_ts_millis(run.info.start_time),
            "run_start_time": run_start_time_str
        }
        _logger.info(f"Not exporting run: {msg}")
        return
    is_success = export_run(
        run_id = run.info.run_id,
        output_dir = os.path.join(output_dir, run.info.run_id),
        export_deleted_runs = export_deleted_runs,
        notebook_formats = notebook_formats,
        mlflow_client = mlflow_client
    )
    if is_success:
        ok_run_ids.append(run.info.run_id)
    else:
        failed_run_ids.append(run.info.run_id)


def _get_runs(mlflow_client, run_ids, exp, failed_run_ids):
    runs = []
    for run_id in run_ids:
        try:
            run = mlflow_client.get_run(run_id)
            if run.info.experiment_id == exp.experiment_id:
                runs.append(run)
            else:
                msg = {
                   "run_id": {run.info.run_id},
                    "run.experiment_id": {run.info.experiment_id},
                    "experiment_id": {exp.experiment_id}
                }
                _logger.warning(f"Not exporting run since it doesn't belong to experiment: {msg}")
                failed_run_ids.append(run.info.run_id)
        except Exception as e:
            msg = { "run_id": run_id, "experiment_id": exp.experiment_id, "Exception": e }
            _logger.warning(f"Run export failed: {msg}")
            failed_run_ids.append(run_id)
    return runs


@click.command()
@opt_experiment
@opt_output_dir
@opt_run_ids
@opt_export_permissions
@opt_run_start_time
@opt_export_deleted_runs
@opt_check_nested_runs
@opt_notebook_formats

def main(experiment, output_dir, run_ids, export_permissions, run_start_time, export_deleted_runs, check_nested_runs, notebook_formats):
    _logger.info("Options:")
    for k,v in locals().items():
        _logger.info(f"  {k}: {v}")

    if run_ids:
        run_ids = run_ids.split(",")

    export_experiment(
        experiment_id_or_name = experiment,
        output_dir = output_dir,
        run_ids = run_ids,
        export_permissions = export_permissions,
        run_start_time = run_start_time,
        export_deleted_runs = export_deleted_runs,
        check_nested_runs = check_nested_runs,
        notebook_formats = utils.string_to_list(notebook_formats)
    )


if __name__ == "__main__":
    main()
