""" 
Sample post-processing rewriters for models and experiments:
  1. for registered model truncate versions to one
  2. for experiment truncate runs to one
"""

import os
from mlflow_export_import.common import io_utils


def rewrite_model(model_dct, models_dir):
    """ processes model.json """
    versions = model_dct["mlflow"]["registered_model"]["versions"]
    print(f"  Original versions: {len(versions)}")
    versions = versions[:1]
    print(f"  New versions: {len(versions)}")
    model_dct["mlflow"]["registered_model"]["versions"] = versions


def rewrite_experiment(experiment_dct, experiment_dir):
    """ processes experiment.json """
    def fmt_run(run_dct):
        from mlflow_export_import.common.timestamp_utils import fmt_ts_millis
        info = run_dct["info"]
        return f'run_id: {info["run_id"]} start_time: {info["start_time"]} {fmt_ts_millis(info["start_time"])}'
    runs = experiment_dct["mlflow"]["runs"]
    print(f"  Original runs: {len(runs)}")

    # do some custom processing such as returning the latest run
    latest_run_dct = None
    for run_id in runs:
        path = os.path.join(experiment_dir, run_id, "run.json")
        run_dct = io_utils.read_file(path)["mlflow"]
        if not latest_run_dct:
            latest_run_dct = run_dct
        else if latest_run_dct is not None and latest_run_dct["info"]["start_time"] > run_dct["info"]["start_time"]:
            latest_run_dct = run_dct
        print(f"    Run: {fmt_run(run_dct)}")
    print(f"  Latest run: {fmt_run(latest_run_dct)}")
    runs = [ latest_run_dct ]
    print(f"  New runs: {len(runs)}")

    experiment_dct["mlflow"]["runs"] = runs

