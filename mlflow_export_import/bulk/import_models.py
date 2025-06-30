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
    opt_import_permissions,
    opt_import_source_tags,
    opt_experiment_rename_file,
    opt_model_rename_file,
    opt_use_threads
)
from mlflow_export_import.common import utils, io_utils
from mlflow_export_import.client.client_utils import create_mlflow_client
from mlflow_export_import.model.import_model import BulkModelImporter
from mlflow_export_import.bulk.import_experiments import import_experiments
from mlflow_export_import.bulk import rename_utils

_logger = utils.getLogger(__name__)


def import_models(
        input_dir,
        delete_model,
        import_permissions = False,
        import_source_tags = False,
        use_src_user_id = False,
        experiment_renames = None,
        model_renames = None,
        verbose = False,
        use_threads = False,
        mlflow_client = None,
        target_model_catalog = None,    #birbal added
        target_model_schema = None      #birbal added
    ):
    mlflow_client = mlflow_client or create_mlflow_client()
    experiment_renames = rename_utils.get_renames(experiment_renames)
    model_renames = rename_utils.get_renames(model_renames)
    start_time = time.time()
    exp_run_info_map, exp_info = _import_experiments(
        mlflow_client,
        input_dir,
        experiment_renames,
        import_permissions,
        import_source_tags,
        use_src_user_id,
        use_threads
    )
    run_info_map = _flatten_run_info_map(exp_run_info_map)
    model_res = _import_models(
        mlflow_client,
        input_dir,
        run_info_map,
        delete_model,
        import_permissions,
        import_source_tags,
        model_renames,
        experiment_renames,
        verbose,
        use_threads,
        target_model_catalog, #birbal added
        target_model_schema     #birbal added
    )
    duration = round(time.time()-start_time, 1)
    dct = { "duration": duration, "experiments_import": exp_info, "models_import": model_res }
    _logger.info("\nImport report:")
    _logger.info(f"{json.dumps(dct,indent=2)}\n")


def _flatten_run_info_map(exp_run_info_map):
    run_info_map = {}
    for dct in exp_run_info_map.values():
        if dct:
            for src_run_id, dst_run_info in dct.items():
                run_info_map[src_run_id] =  dst_run_info
    return run_info_map


def _import_experiments(mlflow_client,
        input_dir,
        experiment_renames,
        import_permissions,
        import_source_tags,
        use_src_user_id,
        use_threads
    ):
    start_time = time.time()

    exp_run_info_map = import_experiments(
        input_dir = os.path.join(input_dir,"experiments"),
        import_permissions = import_permissions,
        import_source_tags = import_source_tags,
        use_src_user_id = use_src_user_id,
        experiment_renames = experiment_renames,
        use_threads = use_threads,
        mlflow_client = mlflow_client
    )
    duration = round(time.time()-start_time, 1)

    exp_run_info_map_ok = {}
    num_exceptions = 0
    for x in exp_run_info_map:
        if x:
            exp_id, run_info_map = x[0], x[1]
            exp_run_info_map_ok[exp_id] = run_info_map
        else:
            num_exceptions += 1

    if num_exceptions > 0:
        _logger.warning(f"Errors: {num_exceptions}")
    _logger.info(f"Duration: {duration} seconds")

    return exp_run_info_map_ok, {
        "experiments": len(exp_run_info_map),
        "exceptions": num_exceptions,
        "duration": duration
    }


def _import_models(mlflow_client,
        input_dir,
        run_info_map,
        delete_model,
        import_permissions,
        import_source_tags,
        model_renames,
        experiment_renames,
        verbose,
        use_threads,
        target_model_catalog = None,    #birbal added
        target_model_schema = None      #birbal added
    ):
    max_workers = utils.get_threads(use_threads)
    start_time = time.time()

    models_dir = os.path.join(input_dir, "models")
    models = io_utils.read_file_mlflow(os.path.join(models_dir,"models.json"))
    model_names = models["models"]
    all_importer = BulkModelImporter(
        mlflow_client = mlflow_client,
        run_info_map = run_info_map,
        import_permissions = import_permissions,
        import_source_tags = import_source_tags,
        experiment_renames = experiment_renames
    )

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for model_name in model_names:
            _logger.info(f"model name BEFORE rename : '{model_name}'")  #birbal added
            dir = os.path.join(models_dir, model_name)
            model_name = rename_utils.rename(model_name, model_renames, "model")

            if target_model_catalog is not None and target_model_schema is not None: #birbal added
                model_name=rename_utils.build_full_model_name(target_model_catalog, target_model_schema, model_name)
            _logger.info(f"model name AFTER rename : '{model_name}'")   #birbal added
            
            executor.submit(all_importer.import_model,
               model_name = model_name,
               input_dir = dir,
               delete_model = delete_model,
               verbose = verbose
            )

    duration = round(time.time()-start_time, 1)
    return { "models": len(model_names), "duration": duration }


@click.command()
@opt_input_dir
@opt_delete_model
@opt_import_permissions
@opt_experiment_rename_file
@opt_model_rename_file
@opt_import_source_tags
@opt_use_src_user_id
@opt_use_threads
@opt_verbose

def main(input_dir, delete_model,
        import_permissions,
        experiment_rename_file,
        model_rename_file,
        import_source_tags,
        use_src_user_id,
        use_threads,
        verbose,
    ):
    _logger.info("Options:")
    for k,v in locals().items():
        _logger.info(f"  {k}: {v}")

    import_models(
        input_dir = input_dir,
        delete_model = delete_model,
        import_permissions = import_permissions,
        experiment_renames = rename_utils.get_renames(experiment_rename_file),
        model_renames = rename_utils.get_renames(model_rename_file),
        import_source_tags = import_source_tags,
        use_src_user_id = use_src_user_id,
        verbose = verbose,
        use_threads = use_threads
    )


if __name__ == "__main__":
    main()
