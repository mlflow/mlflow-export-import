"""
Export the entire tracking server - all registerered models, experiments, runs and the Databricks notebook associated with the run.
"""

import os
import time
import click
import mlflow
from mlflow_export_import.bulk.export_models import export_models
from mlflow_export_import.bulk.export_experiments import export_experiments
from mlflow_export_import import click_doc
from mlflow_export_import.bulk import write_export_manifest_file

ALL_STAGES = "Production,Staging,Archive,None" 

def export_all(output_dir, export_metadata_tags=False, notebook_formats="", use_threads=False):
    start_time = time.time()
    client = mlflow.tracking.MlflowClient()
    export_models(
        client,
        model_names="all", 
        output_dir=output_dir,
        notebook_formats=notebook_formats, 
        stages=ALL_STAGES, 
        use_threads=use_threads)
    export_experiments(
        client,
        experiments="all",
        output_dir=os.path.join(output_dir,"experiments"),
        export_metadata_tags=export_metadata_tags,
        notebook_formats=notebook_formats,
        use_threads=use_threads)
    duration = round(time.time() - start_time, 1)
    write_export_manifest_file(output_dir, duration, ALL_STAGES, notebook_formats)
    print(f"Duraton for entire tracking server export: {duration} seconds")

@click.command()
@click.option("--output-dir", 
    help="Output directory.", 
    type=str,
    required=True
)
@click.option("--notebook-formats", 
    help=click_doc.notebook_formats, 
    type=str,
    default="", 
    show_default=True
)
@click.option("--use-threads",
    help=click_doc.use_threads,
    type=bool,
    default=False,
    show_default=True
)

def main(output_dir, notebook_formats, use_threads):
    print("Options:")
    for k,v in locals().items():
        print(f"  {k}: {v}")
    export_all(output_dir, notebook_formats, use_threads)

if __name__ == "__main__":
    main()
