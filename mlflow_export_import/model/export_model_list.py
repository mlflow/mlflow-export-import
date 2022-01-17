"""
Export a registered model and all the experiment runs associated with each version.
"""

import os
import time
import json
import click
import mlflow
from mlflow_export_import.model.export_model import ModelExporter
from mlflow_export_import.common import filesystem as _filesystem
from mlflow_export_import import utils, click_doc

client = mlflow.tracking.MlflowClient()

def export_models(models, output_dir, stages, notebook_formats, export_notebook_revision, export_run=True):
    start_time = time.time()
    if models == "all":
        models = [ model.name for model in client.list_registered_models() ]
    elif models.endswith("*"):
        model_prefix = models[:-1]
        models = [ model.name for model in client.list_registered_models() if model.name.startswith(model_prefix) ] # Wish there was an model search method for efficiency]
    else:
        models = models.split(",")
    print("models:")
    for model in models:
        print(f"  {model}")
    exporter = ModelExporter(stages=stages, notebook_formats=utils.string_to_list(notebook_formats), export_notebook_revision=export_notebook_revision, export_run=export_run)
    for model in models:
        dir = os.path.join(output_dir, model)
        exporter.export_model(dir, model)

    duration = round(time.time() - start_time, 1)
    manifest = {
        "info": {
            "mlflow_version": mlflow.__version__,
            "mlflow_tracking_uri": mlflow.get_tracking_uri(),
            "export_time": utils.get_now_nice(),
            "models": len(models),
            "duration": duration
        },
        "stages": stages,
        "notebook_formats": notebook_formats,
        "export_notebook_revision": export_notebook_revision,
        "models": models
    }

    fs = _filesystem.get_filesystem(output_dir)
    fs.mkdirs(output_dir)
    with open(os.path.join(output_dir, "manifest.json"), "w") as f:
        f.write(json.dumps(manifest, indent=2)+"\n")

    print(f"{len(models)} models exported")
    print(f"Duration: {duration} seonds")

@click.command()
@click.option("--models", help="Registered model names (comma delimited). 'all' will export all experiments.", required=True, type=str)
@click.option("--output-dir", help="Output directory.", required=True, type=str)
@click.option("--stages", help=click_doc.model_stages, required=None, type=str)
@click.option("--notebook-formats", help=click_doc.notebook_formats, default="", show_default=True)
@click.option("--export-notebook-revision", help=click_doc.export_notebook_revision, type=bool, default=False, show_default=True)

def main(models, output_dir, stages, notebook_formats, export_notebook_revision):
    export_models(models, output_dir, stages, notebook_formats, export_notebook_revision)

if __name__ == "__main__":
    print("Options:")
    for k,v in locals().items():
        print(f"  {k}: {v}")
    main()
