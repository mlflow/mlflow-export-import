"""
Exports models and their versions' backing run along with the experiment that the run belongs to.
"""

import os
import time
import click
import mlflow
from mlflow_export_import.model import export_model_list
from mlflow_export_import.experiment import export_experiment_list
from mlflow_export_import import click_doc
from mlflow_export_import.bulk import write_export_manifest_file
from mlflow_export_import.bulk.model_utils import get_experiments_runs_of_models

client = mlflow.tracking.MlflowClient()

def export_all(output_dir, models, stages, notebook_formats, export_notebook_revision):
    exps_and_runs = get_experiments_runs_of_models(models)
    exp_ids = exps_and_runs.keys()
    start_time = time.time()
    export_experiment_list.export_experiment_list(exp_ids, os.path.join(output_dir,"experiments"), True, notebook_formats, export_notebook_revision)
    export_model_list.export_models(models, os.path.join(output_dir,"models"), stages, notebook_formats, export_notebook_revision)
    duration = round(time.time() - start_time, 1)
    write_export_manifest_file(output_dir, duration, stages, notebook_formats, export_notebook_revision)
    print(f"Duration: {duration} seconds")

@click.command()
@click.option("--output-dir", help="Output directory.", required=True, type=str)
@click.option("--models", help="Models to export. Values are 'all', comma seperated list of models or model prefix with * ('sklearn*'). Default is 'all'", default="all", type=str)
@click.option("--stages", help=click_doc.model_stages, required=None, type=str)
@click.option("--notebook-formats", help=click_doc.notebook_formats, default="", show_default=True)
@click.option("--export-notebook-revision", help=click_doc.export_notebook_revision, type=bool, default=False, show_default=True)

def main(output_dir, stages, notebook_formats, export_notebook_revision, models):
    print("Options:")
    for k,v in locals().items():
        print(f"  {k}: {v}")
    export_all(output_dir, models, stages, notebook_formats, export_notebook_revision)

if __name__ == "__main__":
    main()
