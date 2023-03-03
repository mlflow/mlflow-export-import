"""
Tests for importing MLflow run data (params, metrics and tags) that exceed API limits.
See: https://www.mlflow.org/docs/latest/rest-api.html#request-limits.
"""

import mlflow
from mlflow.utils.validation import MAX_PARAMS_TAGS_PER_BATCH, MAX_METRICS_PER_BATCH
from oss_utils_test import create_experiment, create_dst_experiment_name, now
from compare_utils import compare_runs
from mlflow.entities import Metric, Param, RunTag
from mlflow_export_import.run.export_run import RunExporter
from mlflow_export_import.run.import_run import RunImporter
from init_tests import mlflow_context

_num_params = 10
_num_metrics = 10
_num_tags = 10

def test_params(mlflow_context):
    run1, run2 = _init_test_runs(mlflow_context, 
        RunExporter(mlflow_context.client_src), 
        RunImporter(mlflow_context.client_dst, mlmodel_fix=True), 
        num_params=_num_params)
    assert len(run1.data.params) == MAX_PARAMS_TAGS_PER_BATCH + _num_params
    compare_runs(mlflow_context.client_src, mlflow_context.client_dst, run1, run2, mlflow_context.output_dir)

def test_metrics(mlflow_context):
    run1, run2 = _init_test_runs(mlflow_context, 
        RunExporter(mlflow_context.client_src),
        RunImporter(mlflow_context.client_dst, mlmodel_fix=True), 
        num_metrics=_num_metrics)
    assert len(run1.data.metrics) == MAX_METRICS_PER_BATCH + _num_metrics
    compare_runs(mlflow_context.client_src, mlflow_context.client_dst, run1, run2, mlflow_context.output_dir)

def test_tags(mlflow_context):
    run1, run2 = _init_test_runs(mlflow_context, 
        RunExporter(mlflow_context.client_src),
        RunImporter(mlflow_context.client_dst, mlmodel_fix=True), 
        num_tags=_num_tags)
    assert len(run1.data.tags) >= MAX_PARAMS_TAGS_PER_BATCH + _num_tags
    compare_runs(mlflow_context.client_src, mlflow_context.client_dst, run1, run2, mlflow_context.output_dir)

def test_params_and_metrics(mlflow_context):
    run1, run2 = _init_test_runs(mlflow_context, 
        RunExporter(mlflow_context.client_src),
        RunImporter(mlflow_context.client_dst, mlmodel_fix=True), 
        num_params=_num_params, num_metrics=_num_metrics)
    assert len(run1.data.params) == MAX_PARAMS_TAGS_PER_BATCH + _num_params
    assert len(run1.data.metrics) == MAX_METRICS_PER_BATCH + _num_metrics
    compare_runs(mlflow_context.client_src, mlflow_context.client_dst, run1, run2, mlflow_context.output_dir)

def _init_test_runs(mlflow_context, exporter, importer, num_params=None, num_metrics=None, num_tags=None):
    exp, run = _create_run(mlflow_context.client_src, num_params, num_metrics, num_tags)
    exporter.export_run(run.info.run_id, mlflow_context.output_run_dir)

    experiment_name = create_dst_experiment_name(exp.name)
    res = importer.import_run(experiment_name, mlflow_context.output_run_dir)

    run1 = mlflow_context.client_src.get_run(run.info.run_id)
    run2 = mlflow_context.client_dst.get_run(res[0].info.run_id)
    return run1, run2

def _create_run(client, num_params=None, num_metrics=None, num_tags=None):
    exp = create_experiment(client)
    with mlflow.start_run() as run:
        with open("info.txt", "w", encoding="utf-8") as f: f.write("Hi artifact")
        mlflow.log_artifact("info.txt","dir")
    if num_params:
        params0 = [Param(f"p0_{j:>04d}", "pval") for j in range(0,MAX_PARAMS_TAGS_PER_BATCH) ]
        params1 = [Param(f"p1_{j:>04d}", "pval") for j in range(0,num_params) ]
        client.log_batch(run.info.run_id, params=params0)
        client.log_batch(run.info.run_id, params=params1)
    if num_metrics:
        metrics0 = [ Metric(f"m0_{j:>04d}", 0.87, now(), 0) for j in range(0,MAX_METRICS_PER_BATCH) ]
        metrics1 = [ Metric(f"m1_{j:>04d}", 0.87, now(), 0) for j in range(0,num_metrics) ]
        client.log_batch(run.info.run_id, metrics=metrics0)
        client.log_batch(run.info.run_id, metrics=metrics1)
    if num_tags:
        tags0 = [RunTag(f"t0_{j:>04d}", "tval") for j in range(0,MAX_PARAMS_TAGS_PER_BATCH) ]
        tags1 = [RunTag(f"t1_{j:>04d}", "tval") for j in range(0,num_tags) ]
        client.log_batch(run.info.run_id, tags=tags0)
        client.log_batch(run.info.run_id, tags=tags1)

    return exp, run
