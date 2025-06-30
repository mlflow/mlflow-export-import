""" 
Import a list of experiment from a directory.
"""

import os
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
import click

import mlflow
from mlflow_export_import.common.click_options import (
    opt_input_dir, 
    opt_import_permissions,
    opt_import_source_tags,
    opt_use_src_user_id, 
    opt_experiment_rename_file,
    opt_use_threads
)
from mlflow_export_import.common import utils, io_utils
from mlflow_export_import.experiment.import_experiment import import_experiment
from mlflow_export_import.bulk import rename_utils

_logger = utils.getLogger(__name__)


def import_experiments(
        input_dir, 
        import_permissions = False,
        import_source_tags = False,
        use_src_user_id = False, 
        experiment_renames = None,
        use_threads = False,
        mlflow_client = None
    ): 
    """
    :param input_dir: Source experiment directory.
    :param import_permissions: Import Databricks permissions.
    :param import_source_tags: Import source information for MLflow objects and create tags in destination object.
    :param use_src_user_id: Set the destination user ID to the source user ID.
                            Source user ID is ignored when importing into Databricks.
    :param experiment_renames: Experiment rename file.
    :param use_threads: Process in parallel using threads.
    :param mlflow_client: MLflow client.
    :return: List of tuples where each tuple is:
       - Experiment ID.
       - Dictionary of source run_id (key) to destination run.info object (value).
    """

    experiment_renames = rename_utils.get_renames(experiment_renames)

    mlflow_client = mlflow_client or mlflow.MlflowClient()
    dct = io_utils.read_file_mlflow(os.path.join(input_dir, "experiments.json"))
    exps = dct["experiments"]
    _logger.info("Importing experiments:")
    for exp in exps:
        _logger.info(f"Importing experiment: {exp}")

    max_workers = utils.get_threads(use_threads)
    futures = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for exp in exps:
            exp_input_dir = os.path.join(input_dir,exp["id"])
            exp_name = exp["name"]
            run_info_map = executor.submit(_import_experiment, 
                mlflow_client, 
                exp_name, 
                exp_input_dir, 
                import_permissions, 
                import_source_tags, 
                use_src_user_id, 
                experiment_renames
            )
            futures.append([exp["id"], run_info_map])
    return [ (f[0], f[1].result()) for f in futures ] # materialize the future


def _import_experiment(mlflow_client, 
        exp_name, 
        input_dir, 
        import_permissions, 
        import_source_tags, 
        use_src_user_id, 
        experiment_renames
    ):
    """
    :return: 
       - Dictionary of source run_id (key) to destination run.info object (value).
       - None if error happened
    """
    try:
        exp_name =  rename_utils.rename(exp_name, experiment_renames, "experiment")
        run_info_map = import_experiment(
            mlflow_client = mlflow_client,
            experiment_name = exp_name,
            input_dir = input_dir,
            import_permissions = import_permissions,
            import_source_tags = import_source_tags,
            use_src_user_id = use_src_user_id
        )
        return run_info_map
    except Exception as e:
        msg = { "experiment": exp_name, "Exception": str(e) }
        import traceback
        traceback.print_exc()
        _logger.error(f"Failed to import experiment: {msg}")
        return None


@dataclass()
class ImportResult:
    run_info_map: dict
    exception: None

@click.command()
@opt_input_dir
@opt_import_permissions
@opt_import_source_tags
@opt_use_src_user_id
@opt_experiment_rename_file
@opt_use_threads

def main(input_dir, import_permissions, import_source_tags, use_src_user_id, experiment_rename_file, use_threads): 
    _logger.info("Options:")
    for k,v in locals().items():
        _logger.info(f"  {k}: {v}")

    import_experiments(
        input_dir = input_dir, 
        import_permissions = import_permissions,
        import_source_tags = import_source_tags,
        use_src_user_id = use_src_user_id,
        experiment_renames = experiment_rename_file,
        use_threads = use_threads
    )


if __name__ == "__main__":
    main()
