"""
Databricks notebook tests for MLflow export import notebooks.
"""

import os
import mlflow
from init_tests import test_context
from databricks_cli.dbfs.api import DbfsPath
from mlflow_export_import.common import mlflow_utils
from compare_utils import compare_runs_with_source_tags, compare_models
import utils_test

mlflow_client = mlflow.tracking.MlflowClient()


def test_train_model(test_context):
    _run_job(test_context, test_context.tester.run_training_job, "Train model")


def test_export_run(test_context):
    _bounce_dbfs_dir(test_context, test_context.tester.dst_run_base_dir)
    _run_job(test_context, test_context.tester.run_export_run_job, "Export Run")
    _check_dbfs_dir_after_export(test_context, test_context.tester.dst_run_base_dir)


def test_import_run(test_context):
    _run_job(test_context, test_context.tester.run_import_run_job, "Import Run")
    src_run = mlflow_utils.get_last_run(mlflow_client, test_context.tester.ml_exp_path)
    dst_run = mlflow_utils.get_last_run(mlflow_client, test_context.tester.mk_imported_name(test_context.tester.ml_exp_path+"_run"))
    compare_runs_with_source_tags(mlflow_client, mlflow_client, src_run, dst_run, test_context.tester.local_artifacts_compare_dir)


def test_export_experiment_job(test_context):
    _bounce_dbfs_dir(test_context, test_context.tester.dst_exp_base_dir)
    _run_job(test_context, test_context.tester.run_export_experiment_job, "Export Experiment")
    _check_dbfs_dir_after_export(test_context, test_context.tester.dst_exp_base_dir)


def test_import_experiment_job(test_context):
    _run_job(test_context, test_context.tester.run_import_experiment_job, "Import Experiment")
    exp_name_1 = test_context.tester.ml_exp_path
    exp_name_2 = test_context.tester.mk_imported_name(test_context.tester.ml_exp_path)
    exp1 = mlflow_client.get_experiment_by_name(exp_name_1)
    exp2 = mlflow_client.get_experiment_by_name(exp_name_2)
    runs1 = mlflow_client.search_runs(exp1.experiment_id)
    runs2 = mlflow_client.search_runs(exp2.experiment_id)
    assert len(runs1) == len(runs2)
    assert len(runs1) == 1
    compare_runs_with_source_tags(mlflow_client, mlflow_client, runs1[0], runs2[0], _mk_artifact_output(test_context))


def test_export_model(test_context):
    _bounce_dbfs_dir(test_context, test_context.tester.dst_model_base_dir)
    _run_job(test_context, test_context.tester.run_export_model_job, "Export Model")
    _check_dbfs_dir_after_export(test_context, test_context.tester.dst_exp_base_dir)


def test_import_model_job(test_context):
    _run_job(test_context, test_context.tester.run_import_model_job, "Import Experiment")
    model_name_1 = test_context.tester.model_name
    model_name_2 = test_context.tester.mk_imported_name(model_name_1)
    model1 = mlflow_client.get_registered_model(model_name_1)
    model2 = mlflow_client.get_registered_model(model_name_2)
    compare_models(mlflow_client, mlflow_client, model1, model2, test_context.tester.local_artifacts_compare_dir)


def _run_job(test_context, job, name):
    run = test_context.tester.run_job(job, name)
    assert run["state"]["result_state"] == "SUCCESS"
    return run


def _check_dbfs_dir_after_export(test_context, dir):
    """ Minimal check to see if we have created the MLflow object's export directory. More checks needed. """
    files = test_context.dbfs_api.list_files(DbfsPath(dir))
    assert len(files) > 0
    sub_dir = files[0]
    files = test_context.dbfs_api.list_files(sub_dir.dbfs_path)
    assert len(files) > 0


def _mk_artifact_output(test_context):
    dir = os.path.join(test_context.tester.local_artifacts_compare_dir, "artifacts")
    utils_test.create_output_dir(dir)
    return dir

def _bounce_dbfs_dir(test_context, dir):
    pass # TODO
