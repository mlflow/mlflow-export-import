"""
These tests test the MLflow object (Run, Experiment, Registered Model) iterators for one MLflow client.
"""
import mlflow
from mlflow_export_import.common.iterators import SearchRunsIterator
from mlflow_export_import.common.iterators import SearchRegisteredModelsIterator
from mlflow_export_import.common.iterators import ListExperimentsIterator
from mlflow_export_import.common.iterators import ListRegisteredModelsIterator
from utils_test import create_experiment, delete_experiments, delete_models, mk_test_object_name, list_experiments, TEST_OBJECT_PREFIX
from init_tests import mlflow_context

# ==== List experiments

def _create_experiment(client, num_runs=5):
    experiment = create_experiment(client)
    for _ in range(0, num_runs):
        with mlflow.start_run():
            mlflow.log_metric("m1", 0.1)
    return experiment

def _create_experiments(client, num_experiments):
    delete_experiments(client)
    experiments = list_experiments(client)
    assert len(experiments) == 0
    for _ in range(0,num_experiments):
        _create_experiment(client)

def _run_test_list_experiments(client, num_experiments, max_results):
    _create_experiments(client, num_experiments)
    experiments1 = list_experiments(client)
    experiments2 = ListExperimentsIterator(client, max_results)
    assert len(experiments1) == len(list(experiments2))

def test_list_experiments_max_results_LT_num_experiments(mlflow_context):
    _run_test_list_experiments(mlflow_context.client_src, 10, 5)

def test_list_experiments_max_results_EQ_num_experiments(mlflow_context):
    _run_test_list_experiments(mlflow_context.client_src, 10, 10)

def test_list_experiments_max_results_GT_num_experiments(mlflow_context):
    _run_test_list_experiments(mlflow_context.client_src, 10, 20)

def test_list_experiments_max_results_custom(mlflow_context):
    num_experiments = 101
    max_results = 20
    _create_experiments(mlflow_context.client_src, num_experiments)
    experiments1 = list_experiments(mlflow_context.client_src)
    assert len(experiments1) == num_experiments
    experiments2 = ListExperimentsIterator(mlflow_context.client_src, max_results)
    assert len(experiments1) == len(list(experiments2))

# ==== List registered models

def _create_models(client, num_models):
    delete_models(client)
    models = client.list_registered_models()
    assert len(models) == 0
    for _ in range(0,num_models):
        model_name = mk_test_object_name()
        client.create_registered_model(model_name)

def _run_test_list_models(client, num_models, max_results):
    _create_models(client, num_models)
    models1 = client.list_registered_models()
    assert len(models1) == num_models
    models2 = ListRegisteredModelsIterator(client, max_results)
    assert len(models1) == len(list(models2))

def test_list_models_max_results_LT_num_models(mlflow_context):
    _run_test_list_models(mlflow_context.client_src, 10, 5)

def test_list_models_max_results_EQ_num_models(mlflow_context):
    _run_test_list_models(mlflow_context.client_src, 10, 10)

def test_list_models_max_results_GT_num_models(mlflow_context):
    _run_test_list_models(mlflow_context.client_src, 10, 20)

def test_list_models_max_results_custom(mlflow_context):
    num_models = 101
    max_results = 20
    _create_models(mlflow_context.client_src, num_models)
    models1 = mlflow_context.client_src.list_registered_models(max_results=num_models)
    assert len(models1) == num_models
    models2 = ListRegisteredModelsIterator(mlflow_context.client_src, max_results)
    assert len(models1) == len(list(models2))

def test_list_models_max_results_non_default(mlflow_context):
    MAX_RESULTS_DEFAULT = 100
    num_models = 101
    max_results = 20
    _create_models(mlflow_context.client_src, num_models)
    models1 = mlflow_context.client_src.list_registered_models()
    assert len(models1) == MAX_RESULTS_DEFAULT
    models2 = ListRegisteredModelsIterator(mlflow_context.client_src, max_results)
    assert len(list(models2)) == num_models

# ==== SearchRunsIterator

def _create_runs(client, num_runs):
    exp = create_experiment(client, )
    for _ in range(0, num_runs):
        with mlflow.start_run():
            mlflow.log_metric("m1", 0.1)
    return exp

def test_SearchRunsIterator(mlflow_context):
    num_runs = 120
    max_results = 22
    exp = _create_runs(mlflow_context.client_src, num_runs)
    infos = mlflow_context.client_src.list_run_infos(exp.experiment_id)
    assert num_runs == len(infos)
    iterator = SearchRunsIterator(mlflow_context.client_src, exp.experiment_id, max_results)
    runs = list(iterator)
    assert num_runs == len(runs)

def test_SearchRunsIterator_empty(mlflow_context):
    num_runs = 0
    max_results = 22
    exp = _create_runs(mlflow_context.client_src, num_runs)
    infos = mlflow_context.client_src.list_run_infos(exp.experiment_id)
    assert num_runs == len(infos)
    iterator = SearchRunsIterator(mlflow_context.client_src, exp.experiment_id, max_results)
    runs = list(iterator)
    assert num_runs == len(runs)

# Stress test - connection timeout
def test_SearchRunsIterator_many(mlflow_context):
    num_runs = 1200
    max_results = 500
    exp = _create_runs(mlflow_context.client_src, num_runs)
    infos = mlflow_context.client_src.list_run_infos(exp.experiment_id)
    assert len(infos) == 1000
    iterator = SearchRunsIterator(mlflow_context.client_src, exp.experiment_id, max_results)
    runs = list(iterator)
    assert num_runs == len(runs)

# ==== SearchRegisteredModelsIterator

def _init_test_SearchRegisteredModelsIterator(client):
    delete_experiments(client)
    delete_models(client)

def test_SearchRegisteredModelsIterator_all(mlflow_context):
    _init_test_SearchRegisteredModelsIterator(mlflow_context.client_src)
    num_models = 100
    max_results = 20
    _create_models(mlflow_context.client_src, num_models)

    models1 = ListRegisteredModelsIterator(mlflow_context.client_src, max_results)
    models1 = list(models1)
    assert num_models == len(models1)
    models2 = SearchRegisteredModelsIterator(mlflow_context.client_src, max_results)
    assert len(models1) == len(list(models2))

def test_SearchRegisteredModelsIterator_like(mlflow_context):
    _init_test_SearchRegisteredModelsIterator(mlflow_context.client_src)
    num_models = 10
    max_results = 5
    _create_models(mlflow_context.client_src, num_models)
    models = list(ListRegisteredModelsIterator(mlflow_context.client_src, max_results))
    new_prefix = f"{TEST_OBJECT_PREFIX}_new"
    for j in range(0,4):
        new_name = models[j].name.replace(TEST_OBJECT_PREFIX, new_prefix)
        mlflow_context.client_src.rename_registered_model(models[j].name, new_name)
    filter = f"name like '{new_prefix}%'"
    models2 = SearchRegisteredModelsIterator(mlflow_context.client_src, max_results, filter)
    assert 4 == len(list(models2))
