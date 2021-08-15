""" 
Exports a list of experiments to a directory.
"""

import os
import json
import mlflow
import click
from mlflow_export_import.common import mlflow_utils
from mlflow_export_import import utils, click_doc
from mlflow_export_import.experiment.export_experiment import ExperimentExporter

def export_experiment_list(experiments, output_dir, export_metadata_tags, notebook_formats):
    client = mlflow.tracking.MlflowClient()

    if experiments == "all":
        experiments = [ exp.experiment_id for exp in client.list_experiments() ]
    else:
        experiments = experiments.split(",")
    print("Experiments:")
    for exp in experiments:
        print(f"  {exp}")

    exporter = ExperimentExporter(client, export_metadata_tags, utils.string_to_list(notebook_formats))
    lst = []
    for exp_id_or_name in experiments:
        exp = mlflow_utils.get_experiment(client, exp_id_or_name)
        exp_output = os.path.join(output_dir, exp.experiment_id)
        try:
            lst.append( { "id" : exp.experiment_id, "name": exp.name } )
            exporter.export_experiment(exp.experiment_id, exp_output)
        except Exception:
            import traceback
            traceback.print_exc()

    dct = { 
        "info": {
            "mlflow_version": mlflow.__version__,
            "mlflow_tracking_uri": mlflow.get_tracking_uri(),
            "export_time": utils.get_now_nice()
        },
        "experiments": lst 
    }
    with open(os.path.join(output_dir, "manifest.json"), "w") as f:
        f.write(json.dumps(dct,indent=2)+"\n")

@click.command()
@click.option("--experiments", help="Experiment names or IDs (comma delimited). 'all' will export all experiments. ", required=True, type=str)
@click.option("--output-dir", help="Output directory.", required=True)
@click.option("--export-metadata-tags", help=click_doc.export_metadata_tags, type=bool, default=False, show_default=True)
@click.option("--notebook-formats", help=click_doc.notebook_formats, default="SOURCE", show_default=True)

def main(experiments, output_dir, export_metadata_tags, notebook_formats): # pragma: no cover
    print("Options:")
    for k,v in locals().items():
        print(f"  {k}: {v}")
    export_experiment_list(experiments, output_dir, export_metadata_tags, notebook_formats)

if __name__ == "__main__":
    main()
