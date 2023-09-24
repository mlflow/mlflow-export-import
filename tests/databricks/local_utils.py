import mlflow
from tests.open_source.oss_utils_test import mk_test_object_name_default
from . import sklearn_utils
from . init_tests import workspace_src


def _mk_experiment_name():
    return f"{workspace_src.base_dir}/{mk_test_object_name_default()}"


def create_experiment(mlflow_client):
    exp_id = mlflow_client.create_experiment(_mk_experiment_name(), tags={"ocean": "southern"})
    return mlflow_client.get_experiment(exp_id)


def create_run(mlflow_client, experiment_id):
    max_depth = 4
    run = mlflow_client.create_run(experiment_id)
    model = sklearn_utils.create_sklearn_model(max_depth)

    model_path = "model.pkl"
    _write_model(model, model_path)
    mlflow_client.log_artifact(run.info.run_id, model_path, "model")

    mlflow_client.log_param(run.info.run_id, "max_depth",max_depth)
    mlflow_client.set_terminated(run.info.run_id)
    return run.info.run_id

def _write_model(model, path):
    import cloudpickle as pickle
    with open(path,"wb") as f:
        pickle.dump(model, f)
