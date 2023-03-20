import mlflow

from mlflow_export_import.common import utils
from mlflow_export_import.bulk import bulk_utils
from mlflow_export_import.common.iterators import SearchModelVersionsIterator

_logger = utils.getLogger(__name__)


def get_experiments_runs_of_models(client, model_names, show_experiments=False, show_runs=False):
    """ Get experiments and runs to to export. """
    model_names = bulk_utils.get_model_names(client, model_names)
    _logger.info(f"{len(model_names)} Models:")
    for model_name in model_names:
        _logger.info(f"  {model_name}")
    exps_and_runs = {}
    for model_name in model_names:
        versions = SearchModelVersionsIterator(client, filter=f"name='{model_name}'")
        for vr in versions:
            try:
                run = client.get_run(vr.run_id)
                exps_and_runs.setdefault(run.info.experiment_id,[]).append(run.info.run_id)
            except mlflow.exceptions.MlflowException as e:
                if e.error_code == "RESOURCE_DOES_NOT_EXIST":
                    _logger.warning(f"run '{vr.run_id}' of version {vr.version} of model '{model_name}' does not exist")
                else:
                    _logger.warning(f"run '{vr.run_id}' of version {vr.version} of model '{model_name}': Error.code: {e.error_code}. Error.message: {e.message}")
    if show_experiments:
        show_experiments_runs_of_models(exps_and_runs, show_runs)
    return exps_and_runs


def show_experiments_runs_of_models(exps_and_runs, show_runs=False):
    _logger.info("Experiments for models:")
    for k,v in exps_and_runs.items():
        _logger.info(f"  Experiment: {k}")
        for x in v:
            if show_runs: _logger.info(f"    {x}")
