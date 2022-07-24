"""
Exports models and their versions' backing run along with the experiment that the run belongs to.
"""

import os
import json
import time
import click
from concurrent.futures import ThreadPoolExecutor
import mlflow
from mlflow_export_import.model.export_model import ModelExporter
from mlflow_export_import.bulk import export_experiments
from mlflow_export_import.common import filesystem as _filesystem
from mlflow_export_import import utils, click_doc
from mlflow_export_import.bulk import write_export_manifest_file
from mlflow_export_import.bulk.model_utils import get_experiments_runs_of_models
from mlflow_export_import.bulk import bulk_utils

def _export_models(client, model_names, output_dir, export_source_tags, notebook_formats, stages, export_run=True, use_threads=False):
    max_workers = os.cpu_count() or 4 if use_threads else 1
    start_time = time.time()
    model_names = bulk_utils.get_model_names(client, model_names)
    print("Models to export:")
    for model_name in model_names:
        print(f"  {model_name}")

    exporter = ModelExporter(client, 
        export_source_tags=export_source_tags,
        notebook_formats=utils.string_to_list(notebook_formats), 
        stages=stages, export_run=export_run)
    futures = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for model_name in model_names:
            dir = os.path.join(output_dir, model_name)
            future = executor.submit(exporter.export_model, model_name, dir)
            futures.append(future)
    ok_models = [] ; failed_models = []
    for future in futures:
        result = future.result()
        if result[0]: ok_models.append(result[1])
        else: failed_models.append(result[1])

    duration = round(time.time() - start_time, 1)
    manifest = {
        "info": {
            "mlflow_version": mlflow.__version__,
            "mlflow_tracking_uri": mlflow.get_tracking_uri(),
            "export_time": utils.get_now_nice(),
            "total_models": len(model_names),
            "ok_models": len(ok_models),
            "failed_models": len(failed_models),
            "duration": duration
        },
        "stages": stages,
        "notebook_formats": notebook_formats,
        "ok_models": ok_models,
        "failed_models": failed_models
    }

    fs = _filesystem.get_filesystem(output_dir)
    fs.mkdirs(output_dir)
    with open(os.path.join(output_dir, "manifest.json"), "w", encoding="utf-8") as f:
        f.write(json.dumps(manifest, indent=2)+"\n")

    print(f"{len(model_names)} models exported")
    print(f"Duration for registered models export: {duration} seconds")

def export_models(client, model_names, output_dir, export_source_tags=False, notebook_formats=None, stages="", export_all_runs=False, use_threads=False):
    exps_and_runs = get_experiments_runs_of_models(client, model_names)
    exp_ids = exps_and_runs.keys()
    start_time = time.time()
    out_dir = os.path.join(output_dir, "experiments")
    exps_to_export = exp_ids if export_all_runs else exps_and_runs
    export_experiments.export_experiments(client, exps_to_export, out_dir, export_source_tags, notebook_formats, use_threads)
    _export_models(client, model_names, os.path.join(output_dir,"models"), export_source_tags, notebook_formats, stages, export_run=False, use_threads=use_threads)
    duration = round(time.time() - start_time, 1)
    write_export_manifest_file(output_dir, duration, stages, notebook_formats)
    print(f"Duration for total registered models and versions' runs export: {duration} seconds")

@click.command()
@click.option("--output-dir",
     help="Output directory.", 
     type=str,
     required=True
)
@click.option("--models", 
    help="Registered model names (comma delimited).  \
        For example, 'model1,model2'. 'all' will export all models.",
    type=str,
    required=True
)
@click.option("--export-source-tags",
    help=click_doc.export_source_tags,
    type=bool,
    default=False,
    show_default=True
)
@click.option("--notebook-formats", 
    help=click_doc.notebook_formats, 
    type=str,
    default="", 
    show_default=True
)
@click.option("--stages", 
    help=click_doc.model_stages, 
    type=str,
    required=False
)
@click.option("--export-all-runs", 
    help="Export all runs of experiment or just runs associated with registered model versions.", 
    type=bool, 
    default=False, 
    show_default=False
)
@click.option("--use-threads",
    help=click_doc.use_threads,
    type=bool,
    default=False,
    show_default=True
)

def main(models, output_dir, stages, export_source_tags, notebook_formats, export_all_runs, use_threads):
    print(">> models:",models)
    print("Options:")
    for k,v in locals().items():
        print(f"  {k}: {v}")
    client = mlflow.tracking.MlflowClient()
    export_models(client,
        models, 
        output_dir=output_dir, 
        export_source_tags=export_source_tags,
        notebook_formats=notebook_formats, 
        stages=stages, 
        export_all_runs=export_all_runs, 
        use_threads=use_threads)

if __name__ == "__main__":
    main()
