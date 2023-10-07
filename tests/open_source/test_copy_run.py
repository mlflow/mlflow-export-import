from tests.open_source.oss_utils_test import create_simple_run
from tests.compare_utils import compare_runs
from tests.open_source.init_tests import mlflow_context

from mlflow_export_import.copy import copy_run
from tests.open_source.oss_utils_test import mk_test_object_name_default


# == Setup

def _init_run_test(mlflow_context, dst_mlflow_uri=None):
    _, src_run = create_simple_run(mlflow_context.client_src, model_artifact = "model")
    dst_exp_name = mk_test_object_name_default()
    dst_run = copy_run.copy(
        src_run.info.run_id, 
        dst_exp_name, 
        mlflow_context.client_src.tracking_uri,
        dst_mlflow_uri 
    )
    return src_run, dst_run


# == Regular tests
    
def test_run_basic_without_dst_mlflow_uri(mlflow_context): 
    run1, run2 = _init_run_test(mlflow_context)
    compare_runs(mlflow_context, run1, run2)


def test_run_basic_with_dst_mlflow_uri(mlflow_context): 
    run1, run2 = _init_run_test(mlflow_context, mlflow_context.client_dst.tracking_uri)
    compare_runs(mlflow_context, run1, run2)


# == Test for source and exported model prediction equivalence

from tests.sklearn_utils import X_test
import cloudpickle as pickle
import numpy as np


def test_model_predictions(mlflow_context):
    _, run1 = create_simple_run(mlflow_context.client_src)
    run2 = copy_run._copy(run1.info.run_id, mk_test_object_name_default(), mlflow_context.client_src, mlflow_context.client_dst)

    # Since you cannot load model flavors (such as mlflow.sklearn.load_model()) with the MlflowClient,
    # we have to manually load the model pickle file

    path1 = mlflow_context.client_src.download_artifacts(run1.info.run_id, "model/model.pkl")
    with open(path1,"rb") as f:
        model1 = pickle.load(f)
    path2 = mlflow_context.client_src.download_artifacts(run2.info.run_id, "model/model.pkl")
    with open(path2, "rb") as f:
        model2 = pickle.load(f)

    predictions1 = model1.predict(X_test)
    predictions2 = model2.predict(X_test)
    assert np.array_equal(predictions1, predictions2)
