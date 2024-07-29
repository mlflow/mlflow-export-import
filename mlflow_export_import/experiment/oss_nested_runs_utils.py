from mlflow_export_import.common.iterators import SearchRunsIterator


def get_nested_runs(client, runs, parent_runs=None):
    nested_runs = []
    for run in runs:
        nested_runs += _get_nested_runs_for_run(client, run, parent_runs)
    return nested_runs

def get_nested_runs_for_experiment(client, experiment_id):
    filter = f"tags.mlflow.parentRunId like '%'"
    return list(SearchRunsIterator(client, experiment_id, filter=filter))


def _get_nested_runs_for_run(client, run, parent_runs=None):
    nested_runs = _build_nested_runs(client, run.info.experiment_id, parent_runs)
    run_ids =  _get_run_ids(run.info.run_id, nested_runs)
    return [ client.get_run(run_id) for run_id in run_ids ]

def _get_run_ids(root_id, nested_runs):
    nested_run_ids = nested_runs.get(root_id)
    if not nested_run_ids:
        return set()
    all_nested_run_ids = nested_run_ids
    for run_id in nested_run_ids:
        _nested_run_ids = _get_run_ids(run_id, nested_runs)
        if _nested_run_ids:
            all_nested_run_ids += _nested_run_ids
    return set(all_nested_run_ids)

def _build_nested_runs(client, experiment_id, parent_runs=None):
    """
    Flat dict of all descendant run IDs and their child runs
    dict: run_id: list of run_id's child runs (per mlflow.parentRunId tag)
    """
    if not parent_runs:
        parent_runs = get_nested_runs_for_experiment(client, experiment_id)
    dct = { run.info.run_id:run.data.tags["mlflow.parentRunId"] for run in parent_runs }
    nested_runs = {}
    for run_id,parent_id in dct.items():
        nested_runs.setdefault(parent_id, []).append(run_id)
    return nested_runs
