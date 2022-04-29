"""
Imports models and their experiments and runs.
"""

import os
import time
import json
import click
from concurrent.futures import ThreadPoolExecutor
import mlflow
from mlflow_export_import import utils, click_doc
from mlflow_export_import.common import filesystem as _filesystem
from mlflow_export_import.experiment.import_experiment import ExperimentImporter
from mlflow_export_import.model.import_model import AllModelImporter

print("MLflow Tracking URI:", mlflow.get_tracking_uri())

def _remap(run_info_map):
    res = {}
    for dct in run_info_map.values():
        for src_run_id,run_info in dct.items():
            res[src_run_id] = run_info
    return res

def _import_experiments(input_dir, use_src_user_id, import_metadata_tags):
    start_time = time.time()
    manifest_path = os.path.join(input_dir,"experiments","manifest.json")
    manifest = utils.read_json_file(manifest_path)
    exps = manifest["experiments"]
    importer = ExperimentImporter(None, use_src_user_id, import_metadata_tags)
    print("Experiments:")
    for exp in exps: 
        print(" ",exp)
    run_info_map = {}
    exceptions = []
    for exp in exps: 
        exp_input_dir = os.path.join(input_dir, "experiments", exp["id"])
        try:
            _run_info_map = importer.import_experiment( exp["name"], exp_input_dir)
            run_info_map[exp["id"]] = _run_info_map
        except Exception as e:
            exceptions.append(e)
            import traceback
            traceback.print_exc()

    duration = round(time.time() - start_time, 1)
    if len(exceptions) > 0:
        print(f"Errors: {len(exceptions)}")
    print(f"Duration: {duration} seconds")

    return run_info_map, { "experiments": len(exps), "exceptions": exceptions, "duration": duration }

def _import_models(input_dir, run_info_map, delete_model, verbose, use_threads):
    max_workers = os.cpu_count() or 4 if use_threads else 1
    start_time = time.time()
    models_dir = os.path.join(input_dir, "models")
    manifest_path = os.path.join(models_dir,"manifest.json")
    manifest = utils.read_json_file(manifest_path)
    models = manifest["ok_models"]
    importer = AllModelImporter(run_info_map)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for model in models:
            dir = os.path.join(models_dir, model)
            executor.submit(importer.import_model, model, dir, delete_model, verbose)

    duration = round(time.time() - start_time, 1)
    return { "models": len(models), "duration": duration }

def import_all(input_dir, delete_model, use_src_user_id, import_metadata_tags, verbose, use_threads):
    start_time = time.time()
    exp_res = _import_experiments(input_dir, use_src_user_id, import_metadata_tags)
    run_info_map = _remap(exp_res[0])
    model_res = _import_models(input_dir, run_info_map, delete_model, verbose, use_threads)
    duration = round(time.time() - start_time, 1)
    dct = { "duration": duration, "experiment_import": exp_res[1], "model_import": model_res }
    fs = _filesystem.get_filesystem(".")
    utils.write_json_file(fs, "import_report.json", dct)
    print("\nImport report:")
    print(json.dumps(dct,indent=2)+"\n")


@click.command()
@click.option("--input-dir", 
    help="Input directory.", 
    required=True, 
    type=str
)
@click.option("--delete-model", 
    help=click_doc.delete_model, 
    type=bool, 
    default=False, 
    show_default=True
)
@click.option("--verbose", 
    type=bool, 
    help="Verbose.", 
    default=False, 
    show_default=True
)
@click.option("--use-src-user-id", 
    help=click_doc.use_src_user_id, 
    type=bool, 
    default=False, 
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

def main(input_dir, delete_model, use_src_user_id, import_metadata_tags, verbose, use_threads):
    print("Options:")
    for k,v in locals().items():
        print(f"  {k}: {v}")
    import_all(input_dir, 
        delete_model=delete_model, 
        use_src_user_id=use_src_user_id, 
        import_metadata_tags=import_metadata_tags, 
        verbose=verbose, 
        use_threads=use_threads)

if __name__ == "__main__":
    main()
