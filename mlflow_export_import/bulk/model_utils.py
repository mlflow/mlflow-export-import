import mlflow

from mlflow_export_import.common import utils
from mlflow_export_import.bulk import bulk_utils
from mlflow_export_import.common.iterators import SearchModelVersionsIterator

_logger = utils.getLogger(__name__)


def get_experiments_runs_of_models(client, model_names, task_index=None, num_tasks=None, show_experiments=False, show_runs=False):
    """ Get experiments and runs to to export. """
    model_names = bulk_utils.get_model_names(client, model_names, task_index, num_tasks)
    _logger.info(f"TOTAL MODELS TO EXPORT FOR TASK_INDEX={task_index} : {len(model_names)}")
    for model_name in model_names:
        _logger.info(f"  {model_name}")
    exps_and_runs = {}
    for model_name in model_names:
        versions = SearchModelVersionsIterator(client, filter=f""" name="{model_name}" """)      #birbal.Changed from "name='{model_name}'" to handle models name with single quote
        for vr in versions:
            try:
                run = client.get_run(vr.run_id)
                exps_and_runs.setdefault(run.info.experiment_id,[]).append(run.info.run_id)
            except Exception as e:      #birbal added 
                _logger.warning(f"Error with run '{vr.run_id}' of version {vr.version} of model '{model_name}': Error: {e}")
                
    if show_experiments:
        show_experiments_runs_of_models(exps_and_runs, show_runs)
    return exps_and_runs


def get_experiment_runs_dict_from_names(client, experiment_names):  #birbal added entire function
    experiment_runs_dict = {}
    for name in experiment_names:
        experiment = client.get_experiment_by_name(name)
        if experiment is not None:
            experiment_id = experiment.experiment_id
            runs = client.search_runs(experiment_ids=[experiment_id], max_results=1000)
            run_ids = [run.info.run_id for run in runs]
            experiment_runs_dict[experiment_id] = run_ids
        else:
            _logger.info(f"Experiment not found: {name}... in bulk->model_utils.py")

    return experiment_runs_dict


def get_experiments_name_of_models(client, model_names):
    """ Get experiments name to export. """
    model_names = bulk_utils.get_model_names(client, model_names)
    experiment_name_list = []
    for model_name in model_names:
        versions = SearchModelVersionsIterator(client, filter=f""" name="{model_name}" """)     #birbal. Fix for models name with single quote
        for vr in versions:
            try:
                run = client.get_run(vr.run_id)
                experiment_id = run.info.experiment_id                
                experiment = mlflow.get_experiment(experiment_id)
                experiment_name = experiment.name                
                experiment_name_list.append(experiment_name)
            except Exception as e:
                _logger.warning(f"run '{vr.run_id}' of version {vr.version} of model '{model_name}': Error: {e}")
    
    return experiment_name_list



def show_experiments_runs_of_models(exps_and_runs, show_runs=False):
    _logger.info("Experiments for models:")
    for k,v in exps_and_runs.items():
        _logger.info(f"  Experiment: {k}")
        for x in v:
            if show_runs: _logger.info(f"    {x}")
