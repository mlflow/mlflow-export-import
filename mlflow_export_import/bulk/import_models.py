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
    opt_use_threads
)
from mlflow_export_import.common import utils, io_utils
from mlflow_export_import.experiment.import_experiment import import_experiment
from mlflow_export_import.model.import_model import AllModelImporter

_logger = utils.getLogger(__name__)


def _remap(run_info_map):
    res = {}
    for dct in run_info_map.values():
        for src_run_id,run_info in dct.items():
            res[src_run_id] = run_info
    return res


def _import_experiments(mlflow_client, input_dir, use_src_user_id):
    start_time = time.time()

    dct = io_utils.read_file_mlflow(os.path.join(os.path.join(input_dir,"experiments","experiments.json")))
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
                experiment_name = exp["name"], 
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


def _import_models(mlflow_client, input_dir, run_info_map, delete_model, import_source_tags, verbose, use_threads):
    max_workers = os.cpu_count() or 4 if use_threads else 1
    start_time = time.time()

    models_dir = os.path.join(input_dir, "models")
    models = io_utils.read_file_mlflow(os.path.join(os.path.join(models_dir,"models.json")))
    models = models["models"]
    all_importer = AllModelImporter(
        mlflow_client = mlflow_client, 
        run_info_map = run_info_map, 
        import_source_tags = import_source_tags
    )

    if use_threads:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for model in models:
                dir = os.path.join(models_dir, model)
                executor.submit(all_importer.import_model, 
                   model_name = model, 
                   input_dir = dir, 
                   delete_model = delete_model, 
                   verbose = verbose
                )
    else:
        for model in models:
            dir = os.path.join(models_dir, model)
            all_importer.import_model(
                model_name = model, 
                input_dir = dir, 
                delete_model = delete_model, 
                verbose = verbose
            )

    duration = round(time.time()-start_time, 1)
    return { "models": len(models), "duration": duration }


def import_all(
        input_dir, 
        delete_model, 
        import_source_tags = False, 
        use_src_user_id = False, 
        verbose = False, 
        use_threads = False,
        mlflow_client = None
    ):
    mlflow_client = mlflow_client or mlflow.client.MlflowClient()
    start_time = time.time()
    exp_res = _import_experiments(
        mlflow_client, 
        input_dir, 
        use_src_user_id
    )
    run_info_map = _remap(exp_res[0])
    model_res = _import_models(
        mlflow_client, 
        input_dir, 
        run_info_map, 
        delete_model, 
        import_source_tags, 
        verbose, 
        use_threads
    )
    duration = round(time.time()-start_time, 1)
    dct = { "duration": duration, "experiment_import": exp_res[1], "model_import": model_res }
    _logger.info("\nImport report:")
    #_logger.info(json.dumps(dct,indent=2)+"\n")
    _logger.info(f"{json.dumps(dct,indent=2)}\n")


@click.command()
@opt_input_dir
@opt_delete_model
@opt_import_source_tags
@opt_use_src_user_id
@opt_verbose
@opt_use_threads

def main(input_dir, delete_model, import_source_tags, use_src_user_id, verbose, use_threads):
    _logger.info("Options:")
    for k,v in locals().items():
        _logger.info(f"  {k}: {v}")
    import_all(
        input_dir = input_dir,
        delete_model = delete_model, 
        import_source_tags = import_source_tags,
        use_src_user_id = use_src_user_id, 
        verbose = verbose, 
        use_threads = use_threads
    )


if __name__ == "__main__":
    main()
