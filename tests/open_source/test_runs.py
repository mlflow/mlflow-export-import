from mlflow_export_import.run.export_run import RunExporter
from mlflow_export_import.run.import_run import RunImporter
from oss_utils_test import create_simple_run, create_dst_experiment_name
from utils_test import create_output_dir
from compare_utils import compare_runs, compare_runs_with_source_tags
from init_tests import mlflow_context

# == Setup

mlmodel_fix = True

def init_run_test(mlflow_context, exporter, importer, run_name=None, use_metric_steps=False):
    exp, run1 = create_simple_run(mlflow_context.client_src, run_name=run_name, use_metric_steps=use_metric_steps)
    create_output_dir(mlflow_context.output_run_dir)

    exporter.export_run(run1.info.run_id, mlflow_context.output_run_dir)
    experiment_name = create_dst_experiment_name(exp.name)
    run2,_ = importer.import_run(experiment_name, mlflow_context.output_run_dir)

    return run1, run2

# == Regular tests

def test_run_basic(mlflow_context):
    run1, run2 = init_run_test(mlflow_context, 
        RunExporter(mlflow_context.client_src), 
        RunImporter(mlflow_context.client_dst, mlmodel_fix=mlmodel_fix),
        "test_run_basic")
    compare_runs(mlflow_context.client_src, mlflow_context.client_dst, run1, run2, mlflow_context.output_dir)

def test_run_with_source_tags(mlflow_context):
    run1, run2 = init_run_test(mlflow_context, 
        RunExporter(mlflow_context.client_src, export_source_tags=True), 
        RunImporter(mlflow_context.client_dst, mlmodel_fix=mlmodel_fix), 
        "test_run_with_source_tags")
    compare_runs_with_source_tags(mlflow_context.client_src, mlflow_context.client_dst, run1, run2, mlflow_context.output_dir)

def test_run_basic_use_metric_steps(mlflow_context): 
    run1, run2 = init_run_test(mlflow_context, 
        RunExporter(mlflow_context.client_src), 
        RunImporter(mlflow_context.client_dst, mlmodel_fix=mlmodel_fix), 
        run_name="_test_run_basic_use_metric_steps",
        use_metric_steps=True)
    compare_runs(mlflow_context.client_src, mlflow_context.client_dst, run1, run2, mlflow_context.output_dir)

# == Test for source and exported model prediction equivalence

from sklearn.model_selection import train_test_split
from sklearn import datasets
import cloudpickle as pickle
import numpy as np

def test_model_predictions(mlflow_context):
    exp1, run1 = create_simple_run(mlflow_context.client_src)
    run_id1 = run1.info.run_id

    exporter = RunExporter(mlflow_context.client_src)
    exporter.export_run(run_id1, mlflow_context.output_run_dir)

    importer = RunImporter(mlflow_context.client_dst)
    exp_name2 = create_dst_experiment_name(exp1.name)
    res = importer.import_run(exp_name2, mlflow_context.output_run_dir)
    run_id2 = res[0].info.run_id

    # Since you cannot load model flavors (such as mlflow.sklearn.load_model()) with the MlflowClient,
    # we have to manually load the model pickle file

    path1 = mlflow_context.client_src.download_artifacts(run_id1, "model/model.pkl")
    with open(path1,"rb") as f:
        model1 = pickle.load(f)
    path2 = mlflow_context.client_src.download_artifacts(run_id2, "model/model.pkl")
    with open(path2, "rb") as f:
        model2 = pickle.load(f)

    dataset = datasets.load_iris()
    _,X_test, _, _ = train_test_split(dataset.data, dataset.target, test_size=0.3)
    predictions1 = model1.predict(X_test)
    predictions2 = model2.predict(X_test)
    assert np.array_equal(predictions1, predictions2)
