
# Test find_artifacts.find_run_model_names()

import mlflow
from mlflow_export_import.common.find_artifacts import find_run_model_names
from oss_utils_test import create_experiment
from sklearn_utils import create_sklearn_model

client = mlflow.MlflowClient()


def test_no_model():
    create_experiment(client)
    with mlflow.start_run() as run:
        mlflow.set_tag("name","foo")
    model_paths = find_run_model_names(run.info.run_id)
    assert len(model_paths) == 0


def test_one_model():
    create_experiment(client)
    model = create_sklearn_model()
    with mlflow.start_run() as run:
        mlflow.sklearn.log_model(model, "model")
    model_paths = find_run_model_names(run.info.run_id)
    assert len(model_paths) == 1
    assert model_paths[0] == "model"


def test_two_models():
    create_experiment(client)
    model = create_sklearn_model()
    with mlflow.start_run() as run:
        mlflow.sklearn.log_model(model, "model")
        mlflow.sklearn.log_model(model, "model-onnx")
    model_paths = find_run_model_names(run.info.run_id)
    assert len(model_paths) == 2
    assert model_paths[0] == "model"
    assert model_paths[1] == "model-onnx"


def test_two_models_nested():
    create_experiment(client)
    model = create_sklearn_model()
    with mlflow.start_run() as run:
        mlflow.sklearn.log_model(model, "model")
        mlflow.sklearn.log_model(model, "other_models/model-onnx")
    model_paths = find_run_model_names(run.info.run_id)
    assert len(model_paths) == 2
    assert model_paths[0] == "model"
    assert model_paths[1] == "other_models/model-onnx"
