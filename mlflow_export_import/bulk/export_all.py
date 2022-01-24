"""
Export the entire tracking server - all registerered models, experiments, runs and Databricks notebook associated with the run (best effort).
"""

import os
import time
import click
from mlflow_export_import.model import export_model_list
from mlflow_export_import.bulk import export_experiments
from mlflow_export_import import click_doc
from mlflow_export_import.bulk import write_export_manifest_file

ALL_STAGES = "Production,Staging,Archive,None" 

@click.command()
@click.option("--output-dir", help="Output directory.", required=True, type=str)
@click.option("--notebook-formats", help=click_doc.notebook_formats, default="", show_default=True)
@click.option("--export-notebook-revision", help=click_doc.export_notebook_revision, type=bool, default=False, show_default=True)

def main(output_dir, notebook_formats, export_notebook_revision):
    print("Options:")
    for k,v in locals().items():
        print(f"  {k}: {v}")
    start_time = time.time()
    export_experiments.export_experiments("all", os.path.join(output_dir,"experiments"), True, notebook_formats, export_notebook_revision)
    export_model_list.export_models("all", os.path.join(output_dir,"models"), ALL_STAGES, notebook_formats, export_notebook_revision)

    duration = round(time.time() - start_time, 1)
    write_export_manifest_file(output_dir, duration, ALL_STAGES, notebook_formats, export_notebook_revision)
    print(f"Duraton for entire tracking server export: {duration} seconds")

if __name__ == "__main__":
    main()
