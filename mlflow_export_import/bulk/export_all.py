"""
Export the entire tracking server - all registerered models, experiments, runs and the Databricks notebook associated with the run.
"""

import os
import time
import click
import mlflow

from mlflow_export_import.common.click_options import opt_output_dir, opt_notebook_formats, opt_use_threads
from mlflow_export_import.common import io_utils
from mlflow_export_import.bulk.export_models import export_models
from mlflow_export_import.bulk.export_experiments import export_experiments

ALL_STAGES = "Production,Staging,Archived,None" 


def export_all(output_dir, notebook_formats=None, use_threads=False):
    start_time = time.time()
    client = mlflow.tracking.MlflowClient()
    res_models = export_models(
        client,
        model_names="all", 
        output_dir=output_dir,
        notebook_formats=notebook_formats, 
        stages=ALL_STAGES, 
        use_threads=use_threads)
    res_exps = export_experiments(
        client,
        experiments="all",
        output_dir=os.path.join(output_dir,"experiments"),
        notebook_formats=notebook_formats,
        use_threads=use_threads)
    duration = round(time.time() - start_time, 1)

    info_attr = {
        "stages": ALL_STAGES,
        "notebook_formats": notebook_formats,
        "use_threads": use_threads,
        "output_dir": output_dir,
        "duration": duration,
        "models": res_models,
        "experiments": res_exps
    }
    io_utils.write_export_file(output_dir, "manifest.json", __file__, {}, info_attr)
    print(f"Duration for entire tracking server export: {duration} seconds")


@click.command()
@opt_output_dir
@opt_notebook_formats
@opt_use_threads
def main(output_dir, notebook_formats, use_threads):
    print("Options:")
    for k,v in locals().items():
        print(f"  {k}: {v}")
    export_all(output_dir, notebook_formats, use_threads)


if __name__ == "__main__":
    main()
