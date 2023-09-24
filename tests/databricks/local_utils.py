import mlflow
from tests.open_source.oss_utils_test import mk_test_object_name_default
from tests.open_source import sklearn_utils
from . init_tests import workspace_src


def _mk_experiment_name(workspace=workspace_src):
    return f"{workspace.base_dir}/{mk_test_object_name_default()}"


def create_experiment(client):
    exp_id = client.create_experiment(_mk_experiment_name(), tags={"ocean": "southern"})
    return client.get_experiment(exp_id)


def create_run(client, experiment_id):
    max_depth = 4
    model = sklearn_utils.create_sklearn_model(max_depth)
    ori_tracking_uri = mlflow.tracking.get_tracking_uri()
    mlflow.set_tracking_uri(client.tracking_uri)
    with mlflow.start_run(experiment_id=experiment_id) as run:
        mlflow.log_param("max_depth",max_depth)
        mlflow.log_metric("rmse", 0.789)
        mlflow.set_tag("my_tag", "my_val")
        mlflow.sklearn.log_model(model, "model")
        mlflow.set_tag("south_america", "aconcagua")
        with open("info.txt", "w", encoding="utf-8") as f:
            f.write("Hi artifact")
        mlflow.log_artifact("info.txt")
    mlflow.set_tracking_uri(ori_tracking_uri)
    return client.get_run(run.info.run_id)
