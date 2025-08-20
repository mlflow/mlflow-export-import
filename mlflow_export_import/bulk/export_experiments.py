"""
Exports experiments to a directory.
"""

import os
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
import click
import mlflow
from mlflow.exceptions import RestException

from mlflow_export_import.common.click_options import (
    opt_experiments,
    opt_output_dir,
    opt_export_permissions,
    opt_notebook_formats,
    opt_run_start_time,
    opt_export_deleted_runs,
    opt_use_threads
)
from mlflow_export_import.common import MlflowExportImportException
from mlflow_export_import.common import utils, io_utils, mlflow_utils
from mlflow_export_import.common import filesystem as _fs
from mlflow_export_import.bulk import bulk_utils
from mlflow_export_import.experiment.export_experiment import export_experiment
from mlflow_export_import.common.checkpoint_thread import CheckpointThread #birbal added
from queue import Queue     #birbal added

_logger = utils.getLogger(__name__)

def export_experiments(
        experiments,
        output_dir,
        export_permissions = False,
        run_start_time = None,
        export_deleted_runs = False,
        notebook_formats = None,
        use_threads = False,
        mlflow_client = None,
        task_index = None,   #birbal added
        checkpoint_dir_experiment = None   #birbal added
    ):
    """
    :param experiments: Can be either:
      - File (ending with '.txt') containing list of experiment names or IDS
      - List of experiment names
      - List of experiment IDs
      - Dictionary whose key is an experiment id and the value is a list of its run IDs
      - String with comma-delimited experiment names or IDs such as 'sklearn_wine,sklearn_iris' or '1,2'
    :return: Dictionary of summary information
    """

    mlflow_client = mlflow_client or mlflow.MlflowClient()
    start_time = time.time()
    max_workers = utils.get_threads(use_threads)
    experiments_arg = _convert_dict_keys_to_list(experiments.keys())     #birbal added

    if isinstance(experiments,str) and experiments.endswith(".txt"):
        with open(experiments, "r", encoding="utf-8") as f:
            experiments = f.read().splitlines()
        table_data = experiments
        columns = ["Experiment Name or ID"]
        experiments_dct = {}
    else:
        export_all_runs = not isinstance(experiments, dict)
        experiments = bulk_utils.get_experiment_ids(mlflow_client, experiments)

        if export_all_runs:
            table_data = experiments
            columns = ["Experiment Name or ID"]
            experiments_dct = {}
        else:
            experiments_dct = experiments # we passed in a dict
            experiments = experiments.keys()
            table_data = [ [exp_id,len(runs)] for exp_id,runs in experiments_dct.items() ]
            num_runs = sum(x[1] for x in table_data)
            table_data.append(["Total",num_runs])
            columns = ["Experiment ID", "# Runs"]
    utils.show_table("Experiments",table_data,columns)

    if len(experiments) == 0:
        _logger.info(f"NO EXPERIMENTS TO PROCESS")
        return

    ######## birbal new block
    result_queue = Queue()
    checkpoint_thread = CheckpointThread(result_queue, checkpoint_dir_experiment, interval=300, batch_size=100)
    _logger.info(f"checkpoint_thread started for experiments")
    checkpoint_thread.start()
    ########

    ok_runs = 0
    failed_runs = 0
    export_results = []
    futures = []

    try:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for exp_id_or_name in experiments:
                run_ids = experiments_dct.get(exp_id_or_name, [])
                future = executor.submit(_export_experiment,
                    mlflow_client,
                    exp_id_or_name,
                    output_dir,
                    export_permissions,
                    notebook_formats,
                    export_results,
                    run_start_time,
                    export_deleted_runs,
                    run_ids,
                    result_queue #birbal added
                )
                futures.append(future)
        duration = round(time.time() - start_time, 1)
        ok_runs = 0
        failed_runs = 0
        experiment_names = []
        for future in futures:
            result = future.result()
            ok_runs += result.ok_runs
            failed_runs += result.failed_runs
            experiment_names.append(result.name)

        total_runs = ok_runs + failed_runs
        duration = round(time.time() - start_time, 1)

        info_attr = {
            "experiment_names": experiment_names,
            "options": {
                "experiments": experiments_arg,
                "output_dir": output_dir,
                "export_permissions": export_permissions,
                "run_start_time": run_start_time,
                "export_deleted_runs": export_deleted_runs,
                "notebook_formats": notebook_formats,
                "use_threads": use_threads
            },
            "status": {
                "duration": duration,
                "experiments": len(experiments),
                "total_runs": total_runs,
                "ok_runs": ok_runs,
                "failed_runs": failed_runs
            }
        }
        mlflow_attr = { "experiments": export_results }

        # NOTE: Make sure we don't overwrite existing experiments.json generated by export_models when being called by export_all.
        # Merge this existing experiments.json with the new built by export_experiments.
        path = _fs.mk_local_path(os.path.join(output_dir, "experiments.json"))
        if os.path.exists(path):
            from mlflow_export_import.bulk.experiments_merge_utils import merge_mlflow, merge_info
            root = io_utils.read_file(path)
            mlflow_attr = merge_mlflow(io_utils.get_mlflow(root), mlflow_attr)
            info_attr = merge_info(io_utils.get_info(root), info_attr)
            info_attr["note"] = "Merged by export_all from export_models and export_experiments"

        io_utils.write_export_file(output_dir, "experiments.json", __file__, mlflow_attr, info_attr)

        _logger.info(f"{len(experiments)} experiments exported")
        _logger.info(f"{ok_runs}/{total_runs} runs succesfully exported")
        if failed_runs > 0:
            _logger.info(f"{failed_runs}/{total_runs} runs failed")
        _logger.info(f"Duration for {len(experiments)} experiments export: {duration} seconds")

        return info_attr
    
    except Exception as e:  #birbal added
        _logger.error(f"_export_experiment failed: {e}", exc_info=True)
    
    finally: #birbal added
        checkpoint_thread.stop()
        checkpoint_thread.join()
        _logger.info("Checkpoint thread flushed and terminated for experiments") 


def _export_experiment(mlflow_client, exp_id_or_name, output_dir, export_permissions, notebook_formats, export_results,
        run_start_time, export_deleted_runs, run_ids, result_queue = None): #birbal added result_queue = None
    ok_runs = -1; failed_runs = -1
    exp_name = exp_id_or_name
    try:
        if not run_ids:
            _logger.error(f"no runs to export for experiment {exp_id_or_name}. Throwing exception to capture in checkpoint file")
            raise Exception(f"no runs to export for experiment {exp_id_or_name}")

        exp = mlflow_utils.get_experiment(mlflow_client, exp_id_or_name)
        exp_name = exp.name
        exp_output_dir = os.path.join(output_dir, exp.experiment_id)
        start_time = time.time()
        ok_runs, failed_runs = export_experiment(
            experiment_id_or_name = exp.experiment_id,
            output_dir = exp_output_dir,
            run_ids = run_ids,
            export_permissions = export_permissions,
            run_start_time = run_start_time,
            export_deleted_runs = export_deleted_runs,
            notebook_formats = notebook_formats,
            mlflow_client = mlflow_client,
            result_queue = result_queue #birbal added
        )
        duration = round(time.time() - start_time, 1)
        result = {
            "id" : exp.experiment_id,
            "name": exp.name,
            "ok_runs": ok_runs,
            "failed_runs": failed_runs,
            "duration": duration
        }
        export_results.append(result)
        _logger.info(f"Done exporting experiment: {result}")

    except RestException as e:
        mlflow_utils.dump_exception(e)
        err_msg = { **{ "message": "Cannot export experiment", "experiment_id": exp_id_or_name }, ** mlflow_utils.mk_msg_RestException(str(e)) } #birbal type casted
        _logger.error(err_msg)
        err_msg["status"] = "failed"    #birbal added
        result_queue.put(err_msg)   #birbal added
    except MlflowExportImportException as e:
        err_msg = { "message": "Cannot export experiment", "experiment_id": exp_id_or_name, "MlflowExportImportException": str(e.kwargs) }    #birbal string casted
        _logger.error(err_msg)

        err_msg["status"] = "failed"    #birbal added
        result_queue.put(err_msg)   #birbal added
    except Exception as e:
        err_msg = { "message": "Cannot export experiment", "experiment_id": exp_id_or_name, "Exception": str(e) }    #birbal string casted
        _logger.error(err_msg)
        
        err_msg["status"] = "failed"    #birbal added
        result_queue.put(err_msg)   #birbal added

    return Result(exp_name, ok_runs, failed_runs)


def _convert_dict_keys_to_list(obj):
    import collections
    if isinstance(obj, collections.abc.KeysView): # class dict_keys
        obj = list(obj)
    return obj


@dataclass()
class Result:
    name: str = None
    ok_runs: int = 0
    failed_runs: int = 0


@click.command()
@opt_experiments
@opt_output_dir
@opt_export_permissions
@opt_run_start_time
@opt_export_deleted_runs
@opt_notebook_formats
@opt_use_threads

def main(experiments, output_dir, export_permissions, run_start_time, export_deleted_runs, notebook_formats, use_threads):
    _logger.info("Options:")
    for k,v in locals().items():
        _logger.info(f"  {k}: {v}")
    export_experiments(
        experiments = experiments,
        output_dir = output_dir,
        export_permissions = export_permissions,
        run_start_time = run_start_time,
        export_deleted_runs = export_deleted_runs,
        notebook_formats = utils.string_to_list(notebook_formats),
        use_threads = use_threads
    )


if __name__ == "__main__":
    main()
