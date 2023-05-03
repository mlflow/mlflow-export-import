"""
Export the entire tracking server - all registerered models, experiments, runs and the Databricks notebook associated with the run.
"""

import os
import time
import click
import mlflow

from mlflow_export_import.common.click_options import (
    opt_output_dir, 
    opt_export_latest_versions,
    opt_stages,
    opt_export_permissions,
    opt_run_start_time,
    opt_export_deleted_runs,
    opt_notebook_formats, 
    opt_use_threads,
)
from mlflow_export_import.common import utils, io_utils
from mlflow_export_import.bulk.export_models import export_models
from mlflow_export_import.bulk.export_experiments import export_experiments

ALL_STAGES = "Production,Staging,Archived,None" 

_logger = utils.getLogger(__name__)


def export_all(
        output_dir,
        stages = "",
        export_latest_versions = False,
        export_permissions = False,
        run_start_time = None,
        export_deleted_runs = False,
        notebook_formats = None,
        use_threads  =  False,
        mlflow_client = None
    ):
    mlflow_client = mlflow_client or mlflow.MlflowClient()
    start_time = time.time()
    res_models = export_models(
        mlflow_client = mlflow_client,
        model_names = "all", 
        output_dir = output_dir,
        stages = stages,
        export_latest_versions = export_latest_versions,
        export_all_runs = True,
        export_permissions = export_permissions,
        export_deleted_runs = export_deleted_runs,
        notebook_formats = notebook_formats, 
        use_threads = use_threads
    )
    res_exps = export_experiments(
        mlflow_client = mlflow_client,
        experiments = "all",
        output_dir = os.path.join(output_dir,"experiments"),
        export_permissions = export_permissions,
        run_start_time = run_start_time,
        export_deleted_runs = export_deleted_runs,
        notebook_formats = notebook_formats,
        use_threads = use_threads
    )
    duration = round(time.time() - start_time, 1)

    info_attr = {
        "stages": ALL_STAGES,
        "export_latest_versions": export_latest_versions,
        "export_permissions": export_permissions,
        "notebook_formats": notebook_formats,
        "use_threads": use_threads,
        "output_dir": output_dir,
        "duration": duration,
        "models": res_models,
        "experiments": res_exps
    }
    io_utils.write_export_file(output_dir, "manifest.json", __file__, {}, info_attr)
    _logger.info(f"Duration for entire tracking server export: {duration} seconds")


@click.command()
@opt_output_dir
@opt_export_latest_versions
@opt_stages
@opt_export_permissions
@opt_run_start_time
@opt_export_deleted_runs
@opt_notebook_formats
@opt_use_threads

def main(output_dir, stages, export_latest_versions, export_permissions, run_start_time, export_deleted_runs, notebook_formats, use_threads):
    _logger.info("Options:")
    for k,v in locals().items():
        _logger.info(f"  {k}: {v}")
    export_all(
        output_dir = output_dir, 
        stages = stages,
        export_latest_versions = export_latest_versions,
        export_permissions = export_permissions, 
        run_start_time = run_start_time, 
        export_deleted_runs = export_deleted_runs, 
        notebook_formats = notebook_formats, 
        use_threads = use_threads
    )


if __name__ == "__main__":
    main()
