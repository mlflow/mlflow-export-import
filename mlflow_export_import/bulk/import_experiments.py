""" 
Import a list of experiment from a directory.
"""

import os
import json
import click
from concurrent.futures import ThreadPoolExecutor
from mlflow_export_import import click_doc
from mlflow_export_import.experiment.import_experiment import ExperimentImporter

def _import_experiment(importer, exp_name, exp_input_dir):
    try:
        importer.import_experiment(exp_name, exp_input_dir)
    except Exception:
        import traceback
        traceback.print_exc()

def import_experiments(input_dir, experiment_name_prefix, use_src_user_id, import_mlflow_tags, import_metadata_tags, use_threads): 
    path = os.path.join(input_dir,"manifest.json")
    with open(path, "r") as f:
        dct = json.loads(f.read())
    for exp in dct["experiments"]:
        print("  ",exp)

    importer = ExperimentImporter(None,
        use_src_user_id=use_src_user_id,
        import_mlflow_tags=import_mlflow_tags,
        import_metadata_tags=import_metadata_tags)
    max_workers = os.cpu_count() or 4 if use_threads else 1
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for exp in dct["experiments"]:
            exp_input_dir = os.path.join(input_dir,exp["id"])
            exp_name = experiment_name_prefix + exp["name"] if experiment_name_prefix else exp["name"]
            executor.submit(_import_experiment, importer, exp_name, exp_input_dir)

@click.command()
@click.option("--input-dir", 
    help="Input directory.", required=True, type=str
)
@click.option("--experiment-name-prefix", 
    help="If specified, added as prefix to experiment name.", 
    default=None, 
    type=str, 
   show_default=True
)
@click.option("--use-src-user-id", 
    help=click_doc.use_src_user_id, 
    type=bool, 
    default=False, 
   show_default=True
)
@click.option("--import-mlflow-tags", 
    help=click_doc.import_mlflow_tags, 
    type=bool, 
    default=True, 
   show_default=True
)
@click.option("--import-metadata-tags", 
    help=click_doc.import_metadata_tags, 
    type=bool, 
    default=False, 
   show_default=True
)
@click.option("--use-threads",
    help=click_doc.use_threads,
    type=bool,
    default=False,
    show_default=True
)

def main(input_dir, experiment_name_prefix, use_src_user_id, import_mlflow_tags, import_metadata_tags, use_threads): 
    print("Options:")
    for k,v in locals().items():
        print(f"  {k}: {v}")
    import_experiments(input_dir, experiment_name_prefix, use_src_user_id, import_mlflow_tags, import_metadata_tags, use_threads)

if __name__ == "__main__":
    main()
