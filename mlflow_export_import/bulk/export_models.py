"""
Exports models and their versions' backing run along with the experiment that the run belongs to.
"""

import os
import time
import click
from concurrent.futures import ThreadPoolExecutor

import mlflow
from mlflow_export_import.common.click_options import (
    opt_output_dir,
    opt_stages,
    opt_export_latest_versions,
    opt_export_all_runs,
    opt_export_permissions,
    opt_export_deleted_runs,
    opt_export_version_model,
    opt_notebook_formats,
    opt_use_threads
)
from mlflow_export_import.common import utils, io_utils
from mlflow_export_import.client.client_utils import create_mlflow_client
from mlflow_export_import.model.export_model import export_model
from mlflow_export_import.bulk import export_experiments
from mlflow_export_import.bulk.model_utils import get_experiments_runs_of_models
from mlflow_export_import.bulk import bulk_utils
from mlflow_export_import.common.checkpoint_thread import CheckpointThread, filter_unprocessed_objects #birbal added
from queue import Queue     #birbal added

_logger = utils.getLogger(__name__)


def export_models(
        model_names,
        output_dir,
        stages = "",
        export_latest_versions = False,
        export_all_runs = False,
        export_permissions = False,
        export_deleted_runs = False,
        export_version_model = False,
        notebook_formats = None,
        use_threads = False,
        mlflow_client = None,
        task_index = None,  #birbal
        num_tasks = None,   #birbal
        checkpoint_dir_experiment = None,   #birbal
        checkpoint_dir_model = None #birbal
    ):
    """
    :param: model_names: Can be either:
      - Filename (ending with '.txt') containing list of model names
      - List of model names
      - String with comma-delimited model names such as 'model1,model2'
    :return: Dictionary of summary information
    """

    if isinstance(model_names,str) and model_names.endswith(".txt"):
        with open(model_names, "r", encoding="utf-8") as f:
            model_names = f.read().splitlines()

    mlflow_client = mlflow_client or create_mlflow_client()
    exps_and_runs = get_experiments_runs_of_models(mlflow_client, model_names, task_index, num_tasks) ##birbal return dict of key=exp_id and value=list[run_id]

    total_run_ids = sum(len(run_id_list) for run_id_list in exps_and_runs.values()) #birbal added
    _logger.info(f"TOTAL MODEL EXPERIMENTS TO EXPORT FOR TASK_INDEX={task_index}:  {len(exps_and_runs)} AND TOTAL RUN_IDs TO EXPORT: {total_run_ids}") #birbal added
    
    start_time = time.time()
    out_dir = os.path.join(output_dir, "experiments")

    ######Birbal block
    exps_and_runs = filter_unprocessed_objects(checkpoint_dir_experiment,"experiments",exps_and_runs)
    _logger.info(f"AFTER FILTERING OUT THE PROCESSED EXPERIMENTS FROM CHECKPOINT, REMAINING EXPERIMENTS COUNT TO BE PROCESSED: {len(exps_and_runs)} ")  #birbal added
    ######

    # if len(exps_and_runs) == 0:
    #     _logger.info("NO MODEL EXPERIMENTS TO EXPORT")
    #     return


    res_exps = export_experiments.export_experiments(
        mlflow_client = mlflow_client,
        experiments = exps_and_runs,   #birbal added
        output_dir = out_dir,
        export_permissions = export_permissions,
        export_deleted_runs = export_deleted_runs,
        notebook_formats = notebook_formats,
        use_threads = use_threads,
        task_index = task_index,     #birbal added
        checkpoint_dir_experiment = checkpoint_dir_experiment   #birbal added
    )
    res_models = _export_models(
        mlflow_client,
        model_names,
        os.path.join(output_dir,"models"),
        notebook_formats,
        stages,
        use_threads = use_threads,
        export_latest_versions = export_latest_versions,
        export_version_model = export_version_model,
        export_permissions = export_permissions,
        export_deleted_runs = export_deleted_runs,
        task_index = task_index,    #birbal
        num_tasks = num_tasks,  #birbal
        checkpoint_dir_model = checkpoint_dir_model #birbal
    )
    duration = round(time.time()-start_time, 1)
    _logger.info(f"Duration for total registered models and versions' runs export: {duration} seconds")

    info_attr = {
        "model_names": model_names,
        "stages": stages,
        "export_all_runs": export_all_runs,
        "export_latest_versions": export_latest_versions,
        "export_permissions": export_permissions,
        "export_deleted_runs": export_deleted_runs,
        "notebook_formats": notebook_formats,
        "use_threads": use_threads,
        "output_dir": output_dir,
        "models": res_models,
        "experiments": res_exps
    }
    io_utils.write_export_file(output_dir, "manifest.json", __file__, {}, info_attr)

    return info_attr


def _export_models(
        mlflow_client,
        model_names,
        output_dir,
        notebook_formats = None,
        stages = None,
        use_threads = False,
        export_latest_versions = False,
        export_version_model = False,
        export_permissions = False,
        export_deleted_runs = False,
        task_index = None, 
        num_tasks = None,
        checkpoint_dir_model = None
    ):
    max_workers = utils.get_threads(use_threads)
    start_time = time.time()
    model_names = bulk_utils.get_model_names(mlflow_client, model_names, task_index, num_tasks)
    _logger.info(f"TOTAL MODELS TO EXPORT: {len(model_names)}") #birbal added
    _logger.info("Models to export:")
    for model_name in model_names:
        _logger.info(f"  {model_name}")

    futures = []

    ######## birbal new block
    model_names = filter_unprocessed_objects(checkpoint_dir_model,"models",model_names)
    _logger.info(f"AFTER FILTERING OUT THE PROCESSED MODELS FROM CHECKPOINT, TOTAL REMAINING COUNT: {len(model_names)}")
    result_queue = Queue()
    checkpoint_thread = CheckpointThread(result_queue, checkpoint_dir_model, interval=300, batch_size=100)
    _logger.info(f"checkpoint_thread started for models")
    checkpoint_thread.start()
    ########

    try: #birbal added
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for model_name in model_names:
                dir = os.path.join(output_dir, model_name)
                future = executor.submit(export_model,
                    model_name = model_name,
                    output_dir = dir,
                    stages = stages,
                    export_latest_versions = export_latest_versions,
                    export_version_model = export_version_model,
                    export_permissions = export_permissions,
                    export_deleted_runs = export_deleted_runs,
                    notebook_formats = notebook_formats,
                    mlflow_client = mlflow_client,
                    result_queue = result_queue    #birbal added
                )
                futures.append(future)
        ok_models = [] ; failed_models = []
        for future in futures:
            result = future.result()
            if result[0]: ok_models.append(result[1]) 
            else: failed_models.append(result[1])
        duration = round(time.time()-start_time, 1)

        info_attr = {
            "model_names": model_names,
            "stages": stages,
            "export_latest_versions": export_latest_versions,
            "notebook_formats": notebook_formats,
            "use_threads": use_threads,
            "output_dir": output_dir,
            "num_total_models": len(model_names),
            "num_ok_models": len(ok_models),
            "num_failed_models": len(failed_models),
            "duration": duration,
            "failed_models": failed_models
        }
        mlflow_attr = {
            "models": ok_models,
        }
        io_utils.write_export_file(output_dir, "models.json", __file__, mlflow_attr, info_attr)

        _logger.info(f"{len(model_names)} models exported")
        _logger.info(f"Duration for registered models export: {duration} seconds")

        return info_attr
    
    except Exception as e:  #birbal added
        _logger.error(f"export_model failed: {e}")
    
    finally: #birbal added
        checkpoint_thread.stop()
        checkpoint_thread.join()
        _logger.info("Checkpoint thread flushed and terminated for models")


@click.command()
@click.option("--models",
    help="Registered model names (comma delimited) \
 or filename ending with '.txt' containing them.\
 For example, 'model1,model2'. 'all' will export all models.\
 Or 'models.txt' will contain a list of model names.",
    type=str,
    required=True
)
@opt_output_dir
@opt_export_latest_versions
@opt_export_all_runs
@opt_stages
@opt_export_permissions
@opt_export_deleted_runs
@opt_export_version_model
@opt_notebook_formats
@opt_use_threads

def main(models, output_dir, stages, export_latest_versions, export_all_runs,
        export_permissions, export_deleted_runs, export_version_model,
        notebook_formats, use_threads
    ):
    _logger.info("Options:")
    for k,v in locals().items():
        _logger.info(f"  {k}: {v}")
    export_models(
        model_names = models,
        output_dir = output_dir,
        stages = stages,
        export_latest_versions = export_latest_versions,
        export_all_runs = export_all_runs,
        export_permissions = export_permissions,
        export_deleted_runs = export_deleted_runs,
        export_version_model = export_version_model,
        notebook_formats = utils.string_to_list(notebook_formats),
        use_threads = use_threads,
    )


if __name__ == "__main__":
    main()
