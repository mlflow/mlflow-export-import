from mlflow_export_import.run.export_run import RunExporter
from mlflow_export_import.run.import_run import RunImporter
from utils_test import create_simple_run, create_dst_experiment_name, create_output_dir
from compare_utils import compare_runs, compare_run_with_metadata_tags
from init_tests import mlflow_context

# == Setup

mlmodel_fix = True

def init_run_test(mlflow_context, exporter, importer, run_name=None, use_metric_steps=False, verbose=False):
    exp, run1 = create_simple_run(mlflow_context.client_src, run_name=run_name, use_metric_steps=use_metric_steps)
    create_output_dir(mlflow_context.output_run_dir)

    exporter.export_run(run1.info.run_id, mlflow_context.output_run_dir)
    experiment_name = create_dst_experiment_name(exp.name)
    run2,_ = importer.import_run(experiment_name, mlflow_context.output_run_dir)

    return run1, run2

def test_run_basic(mlflow_context):
    run1, run2 = init_run_test(mlflow_context, 
        RunExporter(mlflow_context.client_src), 
        RunImporter(mlflow_context.client_dst, mlmodel_fix=mlmodel_fix),
        "test_run_basic")
    compare_runs(mlflow_context.client_src, mlflow_context.client_dst, mlflow_context.output_dir, run1, run2)

def test_run_with_metadata_tags(mlflow_context):
    run1, run2 = init_run_test(mlflow_context, 
        RunExporter(mlflow_context.client_src, export_metadata_tags=True), 
        RunImporter(mlflow_context.client_dst, mlmodel_fix=mlmodel_fix), 
        "test_run_with_metadata_tags",
        verbose=False)
    compare_run_with_metadata_tags(mlflow_context.client_src, mlflow_context.client_dst, mlflow_context.output_dir, run1, run2)

def test_run_basic_use_metric_steps(mlflow_context): 
    run1, run2 = init_run_test(mlflow_context, 
        RunExporter(mlflow_context.client_src), 
        RunImporter(mlflow_context.client_dst, mlmodel_fix=mlmodel_fix), 
        run_name="_test_run_basic_use_metric_steps",
        use_metric_steps=True)
    compare_runs(mlflow_context.client_src, mlflow_context.client_dst, mlflow_context.output_dir, run1, run2)
