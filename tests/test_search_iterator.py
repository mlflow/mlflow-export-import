import mlflow
from mlflow_export_import.common.search_runs_iterator import SearchRunsIterator
from . utils_test import create_experiment

client = mlflow.tracking.MlflowClient()

def create_runs(num_runs):
    exp = create_experiment()
    for _ in range(0, num_runs):
        with mlflow.start_run():
            mlflow.log_metric("m1", 0.1)
    return exp

def test_search():
    num_runs = 120
    max_results = 22
    exp = create_runs(num_runs)
    infos = client.list_run_infos(exp.experiment_id)
    assert num_runs == len(infos)
    iterator = SearchRunsIterator(client, exp.experiment_id, max_results)
    runs = list(iterator)
    assert num_runs == len(runs)

def test_search_empty():
    num_runs = 0
    max_results = 22
    exp = create_runs(num_runs)
    infos = client.list_run_infos(exp.experiment_id)
    assert num_runs == len(infos)
    iterator = SearchRunsIterator(client, exp.experiment_id, max_results)
    runs = list(iterator)
    assert num_runs == len(runs)

# Stress test - connection timeout
def _test_search_many():
    num_runs = 1200
    max_results = 500
    exp = create_runs(num_runs)
    infos = client.list_run_infos(exp.experiment_id)
    assert len(infos) == 1000
    iterator = SearchRunsIterator(client, exp.experiment_id, max_results)
    runs = list(iterator)
    assert num_runs == len(runs)
