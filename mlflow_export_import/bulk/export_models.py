"""
Exports models and their versions' backing run along with the experiment that the run belongs to.
"""

import os
import time
import click
from concurrent.futures import ThreadPoolExecutor

import mlflow
from mlflow_export_import.common.click_options import (
    opt_output_dir,
    opt_stages,
    opt_export_latest_versions,
    opt_export_all_runs,
    opt_export_permissions,
    opt_run_start_time,
    opt_until,
    opt_export_deleted_runs,
    opt_export_version_model,
    opt_notebook_formats,
    opt_use_threads
)
from mlflow_export_import.common import utils, io_utils
from mlflow_export_import.client.client_utils import create_mlflow_client
from mlflow_export_import.model.export_model import export_model
from mlflow_export_import.bulk import export_experiments
from mlflow_export_import.bulk.model_utils import get_experiments_runs_of_models
from mlflow_export_import.bulk import bulk_utils

_logger = utils.getLogger(__name__)


def export_models(
        model_names,
        output_dir,
        stages = "",
        export_latest_versions = False,
        export_all_runs = False,
        export_permissions = False,
        run_start_time = None,
        runs_until = None,
        export_deleted_runs = False,
        export_version_model = False,
        notebook_formats = None,
        use_threads = False,
        mlflow_client = None
    ):
    """
    :param model_names: Can be either:
      - Filename (ending with '.txt') containing list of model names
      - List of model names
      - String with comma-delimited model names such as 'model1,model2'
    :param output_dir: Output directory
    :param stages: Stages to export (comma separated). Default is all stages.
    :param export_latest_versions: Export latest model versions instead of all versions
    :param export_all_runs: Export all runs of experiment or just runs associated with model versions
    :param export_permissions: Export Databricks permissions
    :param run_start_time: Only export runs started after this UTC time (inclusive). Format: YYYY-MM-DD or YYYY-MM-DD HH:MM:SS
    :param runs_until: Only export runs started before this UTC time (exclusive). Format: YYYY-MM-DD or YYYY-MM-DD HH:MM:SS
    :param export_deleted_runs: Export deleted runs
    :param export_version_model: Export version's cached MLflow model
    :param notebook_formats: Databricks notebook formats to export (comma separated)
    :param use_threads: Process in parallel using threads
    :param mlflow_client: MLflow client
    :return: Dictionary of summary information
    """

    if isinstance(model_names,str) and model_names.endswith(".txt"):
        with open(model_names, "r", encoding="utf-8") as f:
            model_names = f.read().splitlines()

    mlflow_client = mlflow_client or create_mlflow_client()
    exps_and_runs = get_experiments_runs_of_models(mlflow_client, model_names)
    exp_ids = exps_and_runs.keys()
    start_time = time.time()
    out_dir = os.path.join(output_dir, "experiments")
    exps_to_export = exp_ids if export_all_runs else exps_and_runs
    res_exps = export_experiments.export_experiments(
        mlflow_client = mlflow_client,
        experiments = exps_to_export,
        output_dir = out_dir,
        export_permissions = export_permissions,
        run_start_time = run_start_time,
        runs_until = runs_until,
        export_deleted_runs = export_deleted_runs,
        notebook_formats = notebook_formats,
        use_threads = use_threads,
        logged_models_filter = exps_and_runs if not export_all_runs else None
    )
    res_models = _export_models(
        mlflow_client,
        model_names,
        os.path.join(output_dir,"models"),
        notebook_formats,
        stages,
        use_threads = use_threads,
        export_latest_versions = export_latest_versions,
        export_version_model = export_version_model,
        export_permissions = export_permissions,
        export_deleted_runs = export_deleted_runs
    )
    duration = round(time.time()-start_time, 1)
    _logger.info(f"Duration for total registered models and versions' runs export: {duration} seconds")

    info_attr = {
        "model_names": model_names,
        "stages": stages,
        "export_all_runs": export_all_runs,
        "export_latest_versions": export_latest_versions,
        "export_permissions": export_permissions,
        "export_deleted_runs": export_deleted_runs,
        "notebook_formats": notebook_formats,
        "use_threads": use_threads,
        "output_dir": output_dir,
        "models": res_models,
        "experiments": res_exps
    }
    io_utils.write_export_file(output_dir, "manifest.json", __file__, {}, info_attr)

    return info_attr


def _export_models(
        mlflow_client,
        model_names,
        output_dir,
        notebook_formats = None,
        stages = None,
        use_threads = False,
        export_latest_versions = False,
        export_version_model = False,
        export_permissions = False,
        export_deleted_runs = False
    ):
    max_workers = utils.get_threads(use_threads)
    start_time = time.time()
    model_names = bulk_utils.get_model_names(mlflow_client, model_names)
    _logger.info("Models to export:")
    for model_name in model_names:
        _logger.info(f"  {model_name}")

    futures = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for model_name in model_names:
            dir = os.path.join(output_dir, model_name)
            future = executor.submit(export_model,
                model_name = model_name,
                output_dir = dir,
                stages = stages,
                export_latest_versions = export_latest_versions,
                export_version_model = export_version_model,
                export_permissions = export_permissions,
                export_deleted_runs = export_deleted_runs,
                notebook_formats = notebook_formats,
                mlflow_client = mlflow_client,
            )
            futures.append(future)
    ok_models = [] ; failed_models = []
    for future in futures:
        result = future.result()
        if result[0]: ok_models.append(result[1])
        else: failed_models.append(result[1])
    duration = round(time.time()-start_time, 1)

    info_attr = {
        "model_names": model_names,
        "stages": stages,
        "export_latest_versions": export_latest_versions,
        "notebook_formats": notebook_formats,
        "use_threads": use_threads,
        "output_dir": output_dir,
        "num_total_models": len(model_names),
        "num_ok_models": len(ok_models),
        "num_failed_models": len(failed_models),
        "duration": duration,
        "failed_models": failed_models
    }
    mlflow_attr = {
        "models": ok_models,
    }
    io_utils.write_export_file(output_dir, "models.json", __file__, mlflow_attr, info_attr)

    _logger.info(f"{len(model_names)} models exported")
    _logger.info(f"Duration for registered models export: {duration} seconds")

    return info_attr


@click.command()
@click.option("--models",
    help="Registered model names (comma delimited) \
 or filename ending with '.txt' containing them.\
 For example, 'model1,model2'. 'all' will export all models.\
 Or 'models.txt' will contain a list of model names.",
    type=str,
    required=True
)
@opt_output_dir
@opt_export_latest_versions
@opt_export_all_runs
@opt_stages
@opt_export_permissions
@opt_run_start_time
@opt_until
@opt_export_deleted_runs
@opt_export_version_model
@opt_notebook_formats
@opt_use_threads

def main(models, output_dir, stages, export_latest_versions, export_all_runs,
        export_permissions, run_start_time, runs_until, export_deleted_runs, export_version_model,
        notebook_formats, use_threads
    ):
    _logger.info("Options:")
    for k,v in locals().items():
        _logger.info(f"  {k}: {v}")
    export_models(
        model_names = models,
        output_dir = output_dir,
        stages = stages,
        export_latest_versions = export_latest_versions,
        export_all_runs = export_all_runs,
        export_permissions = export_permissions,
        run_start_time = run_start_time,
        runs_until = runs_until,
        export_deleted_runs = export_deleted_runs,
        export_version_model = export_version_model,
        notebook_formats = utils.string_to_list(notebook_formats),
        use_threads = use_threads,
    )


if __name__ == "__main__":
    main()
