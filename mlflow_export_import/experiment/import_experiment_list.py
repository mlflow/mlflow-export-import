""" 
Exports a list of experiment to a directory.
"""

import os
import json
import click

from mlflow_export_import import click_doc
from mlflow_export_import.experiment.import_experiment import ExperimentImporter

@click.command()
@click.option("--input-dir", help="Input directory.", required=True, type=str)
@click.option("--experiment-name-prefix", help="If specified, added as prefix to experiment name.", default=None, type=str, show_default=True)
@click.option("--use-src-user-id", help=click_doc.use_src_user_id, type=bool, default=False, show_default=True)
@click.option("--import-mlflow-tags", help=click_doc.import_mlflow_tags, type=bool, default=True, show_default=True)
@click.option("--import-metadata-tags", help=click_doc.import_metadata_tags, type=bool, default=False, show_default=True)

def main(input_dir, experiment_name_prefix, use_src_user_id, import_mlflow_tags, import_metadata_tags): # pragma: no cover
    print("Options:")
    for k,v in locals().items():
        print(f"  {k}: {v}")

    path = os.path.join(input_dir,"manifest.json")
    with open(path, "r") as f:
        dct = json.loads(f.read())
    for exp in dct["experiments"]:
        print("  ",exp)

    importer = ExperimentImporter(None, use_src_user_id, import_mlflow_tags, import_metadata_tags)
    for exp in dct["experiments"]:
        exp_input = os.path.join(input_dir,exp["id"])
        exp_name = experiment_name_prefix + exp["name"] if experiment_name_prefix else exp["name"]
        importer.import_experiment(exp_name, exp_input)

if __name__ == "__main__":
    main()
