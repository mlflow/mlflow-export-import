import mlflow
from mlflow_export_import.common.iterators import SearchRunsIterator
from mlflow_export_import.common.iterators import SearchRegisteredModelsIterator
from mlflow_export_import.common.iterators import ListExperimentsIterator
from mlflow_export_import.common.iterators import ListRegisteredModelsIterator
from utils_test import create_experiment, delete_experiments, delete_models, mk_test_object_name, list_experiments, TEST_OBJECT_PREFIX

client = mlflow.tracking.MlflowClient()

# ==== List experiments

def _create_experiment(num_runs=5):
    experiment = create_experiment()
    for _ in range(0, num_runs):
        with mlflow.start_run():
            mlflow.log_metric("m1", 0.1)
    return experiment

def _create_experiments(num_experiments):
    delete_experiments()
    experiments = list_experiments()
    assert len(experiments) == 0
    for _ in range(0,num_experiments):
        _create_experiment()

def _run_test_list_experiments(num_experiments, max_results):
    _create_experiments(num_experiments)
    experiments1 = list_experiments()
    experiments2 = ListExperimentsIterator(client, max_results)
    assert len(experiments1) == len(list(experiments2))

def test_list_experiments_max_results_LT_num_experiments():
    _run_test_list_experiments(10, 5)

def test_list_experiments_max_results_EQ_num_experiments():
    _run_test_list_experiments(10, 10)

def test_list_experiments_max_results_GT_num_experiments():
    _run_test_list_experiments(10, 20)

def test_list_experiments_max_results_custom():
    num_experiments = 101
    max_results = 20
    _create_experiments(num_experiments)
    experiments1 = list_experiments()
    assert len(experiments1) == num_experiments
    experiments2 = ListExperimentsIterator(client, max_results)
    assert len(experiments1) == len(list(experiments2))

# ==== List registered models

def _create_models(num_models):
    delete_models()
    models = client.list_registered_models()
    assert len(models) == 0
    for _ in range(0,num_models):
        model_name = mk_test_object_name()
        client.create_registered_model(model_name)

def _run_test_list_models(num_models, max_results):
    _create_models(num_models)
    models1 = client.list_registered_models()
    assert len(models1) == num_models
    models2 = ListRegisteredModelsIterator(client, max_results)
    assert len(models1) == len(list(models2))

def test_list_models_max_results_LT_num_models():
    _run_test_list_models(10, 5)

def test_list_models_max_results_EQ_num_models():
    _run_test_list_models(10, 10)

def test_list_models_max_results_GT_num_models():
    _run_test_list_models(10, 20)

def test_list_models_max_results_custom():
    num_models = 101
    max_results = 20
    _create_models(num_models)
    models1 = client.list_registered_models(max_results=num_models)
    assert len(models1) == num_models
    models2 = ListRegisteredModelsIterator(client, max_results)
    assert len(models1) == len(list(models2))

def test_list_models_max_results_non_default():
    MAX_RESULTS_DEFAULT = 100
    num_models = 101
    max_results = 20
    _create_models(num_models)
    models1 = client.list_registered_models()
    assert len(models1) == MAX_RESULTS_DEFAULT
    models2 = ListRegisteredModelsIterator(client, max_results)
    assert len(list(models2)) == num_models

# ==== SearchRunsIterator

def _create_runs(num_runs):
    exp = create_experiment()
    for _ in range(0, num_runs):
        with mlflow.start_run():
            mlflow.log_metric("m1", 0.1)
    return exp

def test_SearchRunsIterator():
    num_runs = 120
    max_results = 22
    exp = _create_runs(num_runs)
    infos = client.list_run_infos(exp.experiment_id)
    assert num_runs == len(infos)
    iterator = SearchRunsIterator(client, exp.experiment_id, max_results)
    runs = list(iterator)
    assert num_runs == len(runs)

def test_SearchRunsIterator_empty():
    num_runs = 0
    max_results = 22
    exp = _create_runs(num_runs)
    infos = client.list_run_infos(exp.experiment_id)
    assert num_runs == len(infos)
    iterator = SearchRunsIterator(client, exp.experiment_id, max_results)
    runs = list(iterator)
    assert num_runs == len(runs)

# Stress test - connection timeout
def test_SearchRunsIterator_many():
    num_runs = 1200
    max_results = 500
    exp = _create_runs(num_runs)
    infos = client.list_run_infos(exp.experiment_id)
    assert len(infos) == 1000
    iterator = SearchRunsIterator(client, exp.experiment_id, max_results)
    runs = list(iterator)
    assert num_runs == len(runs)

# ==== SearchRegisteredModelsIterator - XX

def _init_test_SearchRegisteredModelsIterator():
    delete_experiments()
    delete_models()

def test_SearchRegisteredModelsIterator_all():
    _init_test_SearchRegisteredModelsIterator()
    num_models = 100
    max_results = 20
    _create_models(num_models)

    models1 = ListRegisteredModelsIterator(client, max_results)
    models1 = list(models1)
    assert num_models == len(models1)
    models2 = SearchRegisteredModelsIterator(client, max_results)
    assert len(models1) == len(list(models2))

def test_SearchRegisteredModelsIterator_like():
    _init_test_SearchRegisteredModelsIterator()
    num_models = 10
    max_results = 5
    _create_models(num_models)
    models = list(ListRegisteredModelsIterator(client, max_results))
    new_prefix = f"{TEST_OBJECT_PREFIX}_new"
    for j in range(0,4):
        new_name = models[j].name.replace(TEST_OBJECT_PREFIX, new_prefix)
        client.rename_registered_model(models[j].name, new_name)
    filter = f"name like '{new_prefix}%'"
    models2 = SearchRegisteredModelsIterator(client, max_results, filter)
    assert 4 == len(list(models2))
