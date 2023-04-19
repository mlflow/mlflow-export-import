from mlflow_export_import.run.export_run import export_run
from mlflow_export_import.run.import_run import import_run
from oss_utils_test import create_simple_run, mk_dst_experiment_name
from utils_test import create_output_dir
from compare_utils import compare_runs
from init_tests import mlflow_context

# == Setup

def init_run_test(mlflow_context, run_name=None, use_metric_steps=False, import_source_tags=False):
    exp, run1 = create_simple_run(mlflow_context.client_src, run_name=run_name, use_metric_steps=use_metric_steps)
    create_output_dir(mlflow_context.output_run_dir)

    export_run(
        run_id = run1.info.run_id, 
        output_dir = mlflow_context.output_run_dir,
        mlflow_client = mlflow_context.client_src
    )
    experiment_name = mk_dst_experiment_name(exp.name)
    run2,_ = import_run(
        experiment_name = experiment_name, 
        input_dir = mlflow_context.output_run_dir,
        import_source_tags = import_source_tags ,
        mlflow_client = mlflow_context.client_dst
    )

    return run1, run2

# == Regular tests

def test_run_basic(mlflow_context):
    run1, run2 = init_run_test(mlflow_context, "test_run_basic")
    compare_runs(mlflow_context.client_src, mlflow_context.client_dst, run1, run2, mlflow_context.output_dir)


def test_run_with_source_tags(mlflow_context):
    run1, run2 = init_run_test(mlflow_context, "test_run_with_source_tags", import_source_tags=True)
    compare_runs(mlflow_context.client_src, mlflow_context.client_dst, run1, run2, mlflow_context.output_dir, import_source_tags=True)


def test_run_basic_use_metric_steps(mlflow_context):
    run1, run2 = init_run_test(mlflow_context,
        run_name = "_test_run_basic_use_metric_steps",
        use_metric_steps = True)
    compare_runs(mlflow_context.client_src, mlflow_context.client_dst, run1, run2, mlflow_context.output_dir)


# == Test for source and exported model prediction equivalence

import sklearn_utils
import cloudpickle as pickle
import numpy as np


def test_model_predictions(mlflow_context):
    exp1, run1 = create_simple_run(mlflow_context.client_src)
    run_id1 = run1.info.run_id

    export_run(
        run_id = run_id1, 
        output_dir = mlflow_context.output_run_dir,
        mlflow_client = mlflow_context.client_src
    )
    exp_name2 = mk_dst_experiment_name(exp1.name)
    res = import_run(
        experiment_name = exp_name2, 
        input_dir = mlflow_context.output_run_dir,
        mlflow_client = mlflow_context.client_dst
    )
    run_id2 = res[0].info.run_id

    # Since you cannot load model flavors (such as mlflow.sklearn.load_model()) with the MlflowClient,
    # we have to manually load the model pickle file

    path1 = mlflow_context.client_src.download_artifacts(run_id1, "model/model.pkl")
    with open(path1,"rb") as f:
        model1 = pickle.load(f)
    path2 = mlflow_context.client_src.download_artifacts(run_id2, "model/model.pkl")
    with open(path2, "rb") as f:
        model2 = pickle.load(f)

    X_test = sklearn_utils.get_prediction_data() 
    predictions1 = model1.predict(X_test)
    predictions2 = model2.predict(X_test)
    assert np.array_equal(predictions1, predictions2)
