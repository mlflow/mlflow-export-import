"""
Imports models and their experiments and runs.
"""

import os
import time
import json
import click
from concurrent.futures import ThreadPoolExecutor

import mlflow
from mlflow_export_import.common.click_options import (
    opt_input_dir,
    opt_delete_model,
    opt_use_src_user_id,
    opt_verbose, 
    opt_import_source_tags, 
    opt_experiment_name_replacements_file,
    opt_model_name_replacements_file,
    opt_use_threads
)
from mlflow_export_import.common import utils, io_utils
from mlflow_export_import.experiment.import_experiment import import_experiment
from mlflow_export_import.model.import_model import AllModelImporter
from mlflow_export_import.bulk import bulk_utils

_logger = utils.getLogger(__name__)


def _remap(run_info_map):
    res = {}
    for dct in run_info_map.values():
        for src_run_id,run_info in dct.items():
            res[src_run_id] = run_info
    return res


def _import_experiments(mlflow_client, input_dir, use_src_user_id, experiment_name_replacements):
    start_time = time.time()

    dct = io_utils.read_file_mlflow(os.path.join(input_dir,"experiments","experiments.json"))
    exps = dct["experiments"]

    _logger.info("Experiments:")
    for exp in exps: 
        _logger.info(f"  {exp}")
    run_info_map = {}
    exceptions = []

    for exp in exps: 
        exp_input_dir = os.path.join(input_dir, "experiments", exp["id"])
        try:
            _run_info_map = import_experiment(
                experiment_name = bulk_utils.replace_name(exp["name"], experiment_name_replacements),
                input_dir = exp_input_dir,
                use_src_user_id = use_src_user_id,
                mlflow_client = mlflow_client
            )
            run_info_map[exp["id"]] = _run_info_map
        except Exception as e:
            exceptions.append(str(e))
            import traceback
            traceback.print_exc()

    duration = round(time.time()-start_time, 1)
    if len(exceptions) > 0:
        _logger.info(f"Errors: {len(exceptions)}")
    _logger.info(f"Duration: {duration} seconds")

    return run_info_map, { "experiments": len(exps), "exceptions": exceptions, "duration": duration }


def _import_models(mlflow_client, input_dir, run_info_map, delete_model, import_source_tags, 
        model_name_replacements, verbose, use_threads
    ):
    max_workers = os.cpu_count() or 4 if use_threads else 1
    start_time = time.time()

    models_dir = os.path.join(input_dir, "models")
    models = io_utils.read_file_mlflow(os.path.join(models_dir,"models.json"))
    model_names = models["models"]
    all_importer = AllModelImporter(
        mlflow_client = mlflow_client, 
        run_info_map = run_info_map, 
        import_source_tags = import_source_tags
    )

    if use_threads:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for model_name in model_names:
                dir = os.path.join(models_dir, model_name)
                executor.submit(all_importer.import_model, 
                   model_name = bulk_utils.replace_name(model_name, model_name_replacements),
                   input_dir = dir,
                   delete_model = delete_model,
                   verbose = verbose
                )
    else:
        for model_name in model_names:
            dir = os.path.join(models_dir, model_name)
            all_importer.import_model(
                model_name = bulk_utils.replace_name(model_name, model_name_replacements),
                input_dir = dir,
                delete_model = delete_model,
                verbose = verbose
            )

    duration = round(time.time()-start_time, 1)
    return { "models": len(model_names), "duration": duration }


def import_all(
        input_dir, 
        delete_model, 
        import_source_tags = False, 
        use_src_user_id = False, 
        experiment_name_replacements = None, 
        model_name_replacements = None, 
        verbose = False, 
        use_threads = False,
        mlflow_client = None
    ):
    mlflow_client = mlflow_client or mlflow.client.MlflowClient()
    start_time = time.time()
    exp_res = _import_experiments(
        mlflow_client, 
        input_dir, 
        use_src_user_id,
        experiment_name_replacements
    )
    run_info_map = _remap(exp_res[0])
    model_res = _import_models(
        mlflow_client, 
        input_dir, 
        run_info_map, 
        delete_model, 
        import_source_tags, 
        model_name_replacements,
        verbose, 
        use_threads
    )
    duration = round(time.time()-start_time, 1)
    dct = { "duration": duration, "experiment_import": exp_res[1], "model_import": model_res }
    _logger.info("\nImport report:")
    _logger.info(f"{json.dumps(dct,indent=2)}\n")


@click.command()
@opt_input_dir
@opt_delete_model
@opt_import_source_tags
@opt_use_src_user_id
@opt_verbose
@opt_experiment_name_replacements_file
@opt_model_name_replacements_file
@opt_use_threads

def main(input_dir, delete_model, import_source_tags, use_src_user_id, 
        experiment_name_replacements_file, 
        model_name_replacements_file, 
        use_threads,
        verbose, 
    ):
    _logger.info("Options:")
    for k,v in locals().items():
        _logger.info(f"  {k}: {v}")

    experiment_name_replacements = None
    if experiment_name_replacements_file:
        experiment_name_replacements = bulk_utils.read_name_replacements_file(experiment_name_replacements_file)

    model_name_replacements = None
    if model_name_replacements_file:
        model_name_replacements = bulk_utils.read_name_replacements_file(model_name_replacements_file)

    import_all(
        input_dir = input_dir,
        delete_model = delete_model, 
        import_source_tags = import_source_tags,
        use_src_user_id = use_src_user_id, 
        experiment_name_replacements = experiment_name_replacements,
        model_name_replacements = model_name_replacements,
        verbose = verbose, 
        use_threads = use_threads
    )


if __name__ == "__main__":
    main()
