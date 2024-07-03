import os
import pandas as pd
import mlflow
from mlflow.models.signature import infer_signature
from mlflow_export_import.model_version.export_model_version import export_model_version
from mlflow_export_import.tools.signature_utils import get_model_signature

from . init_tests import mlflow_context
from . oss_utils_test import mk_test_object_name_default
from . oss_utils_test import create_version

_input_df = pd.read_csv("../data/iris_train.csv")
_output_df = pd.read_csv("../data/iris_score.csv")


def test_set_run_signature(mlflow_context):
    """
    Tests set_signature with runs scheme: 'runs:/73ab168e5775409fa3595157a415bb62/model'
    """
    runs_uri, models_uri, signature, _ = _prep(mlflow_context)
    mlflow.models.set_signature(runs_uri, signature)

    assert get_model_signature(runs_uri)

    # NOTE: when you update a run's model signature, the model version it was created from also gets updated. AFAIK not documented.
    assert get_model_signature(models_uri)


def test_set_model_version_signature(mlflow_context):
    """
    Tests set_signature with models scheme: 'models:/sklearn_wine/1' which is per doc not supported.
    MlflowException: Failed to set signature on "models:/my_model/1". Model URIs with the `models:/` scheme are not supported.
    """

    _, models_uri, signature, _ = _prep(mlflow_context)
    try:
        mlflow.models.set_signature(models_uri, signature)
        assert False
    except mlflow.exceptions.MlflowException as e:
        print(f"EXPECTED ERROR: {type(e)}: {e}")
        assert True


def test_set_file_signature_without_file_scheme(mlflow_context):
    """
    Tests set_signature without file scheme: 'out/run/artifacts/model'
    """
    _run_set_file_signature(mlflow_context, use_file_scheme=False)


def test_set_file_signature_with_file_scheme(mlflow_context):
    """
    Tests set_signature with file scheme: 'file:/opts/mlflow_export_imports/tests/run/artifacts/model'
    """
    _run_set_file_signature(mlflow_context, use_file_scheme=True)


def test_model_signature_get_methods(mlflow_context):
    src_vr, src_run = _create_model_version(mlflow_context)

    runs_uri = f"runs:/{src_run.info.run_id}/model"
    sig1 = get_model_signature(runs_uri, False)
    sig2 = get_model_signature(runs_uri, True)
    assert sig1 == sig2

    models_uri = f"models:/{src_vr.name}/{src_vr.version}"
    sig1 = get_model_signature(models_uri, False)
    sig2 = get_model_signature(models_uri, True)
    assert sig1 == sig2


def _run_set_file_signature(mlflow_context, use_file_scheme=False):
    """
    Tests set_signature with file scheme: 'file:/opts/mlflow_export_imports/tests/run/artifacts/model'
    Tests set_signature without file scheme: 'out/run/artifacts/model'
    """
    _, _, signature, src_vr = _prep(mlflow_context)

    export_model_version(
        model_name = src_vr.name,
        version = src_vr.version,
        output_dir = mlflow_context.output_dir,
        mlflow_client = mlflow_context.client_src
    )
    model_path = os.path.join(mlflow_context.output_dir,"run/artifacts/model")
    file_uri = f"file:{os.path.abspath(model_path)}" if use_file_scheme else model_path

    model_info = mlflow.models.get_model_info(file_uri)
    assert not model_info.signature

    mlflow.models.set_signature(file_uri, signature)

    model_info = mlflow.models.get_model_info(file_uri)
    assert model_info.signature


def _prep(mlflow_context):
    src_vr, src_run = _create_model_version(mlflow_context)

    runs_uri = f"runs:/{src_run.info.run_id}/model"
    assert not get_model_signature(runs_uri)

    models_uri = f"models:/{src_vr.name}/{src_vr.version}"
    assert not get_model_signature(models_uri)

    signature = infer_signature(_input_df, _output_df)
    return runs_uri, models_uri, signature, src_vr


def _create_model_version(mlflow_context):
    model_name_src = mk_test_object_name_default()
    desc = "Hello decription"
    tags = { "city": "kancamagus" }
    mlflow_context.client_src.create_registered_model(model_name_src, tags, desc)
    return create_version(mlflow_context.client_src, model_name_src, "Production")
