from mlflow_export_import.common import utils
from mlflow_export_import.common.iterators import SearchRunsIterator

_logger = utils.getLogger(__name__)


def get_nested_runs(client, runs):
    """
    Return set of run_ids and their nested run descendants from list of run IDs.
    """
    if utils.calling_databricks():
        return get_by_rootRunId(client, runs)
    else:
        #_logger.warning(f"OSS MLflow nested run export not yet supported")
        #return runs
        from . import oss_nested_runs_utils
        descendant_runs = oss_nested_runs_utils.get_descendant_runs(client, runs)
        return runs + descendant_runs


def get_by_rootRunId(client, runs):
    """
    Return list of nested run descendants (includes the root run).
    Unlike Databricks MLflow, OSS MLflow does not add the 'mlflow.rootRunId' tag to child runs.
    """
    descendant_runs= []
    for run in runs:
        filter = f"tags.mlflow.rootRunId = '{run.info.run_id}'"
        _descendant_runs = list(SearchRunsIterator(client, run.info.experiment_id, filter=filter))
        if _descendant_runs:
            descendant_runs += _descendant_runs
        else:
            descendant_runs.append(run)
    return descendant_runs
