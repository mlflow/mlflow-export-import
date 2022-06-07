from mlflow_export_import.run.export_run import RunExporter
from mlflow_export_import.run.import_run import RunImporter
from mlflow_export_import.experiment.export_experiment import ExperimentExporter
from mlflow_export_import.experiment.import_experiment import ExperimentImporter
from utils_test import create_simple_run, init_output_dirs, create_dst_experiment_name
from compare_utils import compare_runs, compare_run_import_metadata_tags
from compare_utils import dump_runs
from init_tests import mlflow_context

# == Setup

mlmodel_fix = True

# == Export/import Run tests

def init_run_test(mlflow_context, exporter, importer, use_metric_steps=False, verbose=False):
    exp, run1 = create_simple_run(mlflow_context.client_src, use_metric_steps)
    exporter.export_run(run1.info.run_id, mlflow_context.output_dir)
    experiment_name = create_dst_experiment_name(exp.name)
    run2,_ = importer.import_run(experiment_name, mlflow_context.output_dir)
    if verbose: dump_runs(run1, run2)
    return run1, run2

def test_run_basic(mlflow_context):
    run1, run2 = init_run_test(mlflow_context, 
        RunExporter(mlflow_context.client_src), 
        RunImporter(mlflow_context.client_dst, mlmodel_fix=mlmodel_fix))
    compare_runs(mlflow_context.client_src, mlflow_context.output_dir, run1, run2)

def test_run_import_metadata_tags(mlflow_context):
    run1, run2 = init_run_test(mlflow_context, 
        RunExporter(mlflow_context.client_src, export_metadata_tags=True), 
        RunImporter(mlflow_context.client_dst, 
        mlmodel_fix=mlmodel_fix, import_metadata_tags=True), verbose=False)
    compare_run_import_metadata_tags(mlflow_context.client_src, mlflow_context.output_dir, run1, run2)

def test_run_basic_use_metric_steps(mlflow_context):
    run1, run2 = init_run_test(mlflow_context, 
        RunExporter(mlflow_context.client_src), 
        RunImporter(mlflow_context.client_dst, 
        mlmodel_fix=mlmodel_fix), use_metric_steps=True)
    compare_runs(mlflow_context.client_src, mlflow_context.output_dir, run1, run2)

# == Export/import Experiment tests

def init_exp_test(mlflow_context, exporter, importer, verbose=False):
    init_output_dirs(mlflow_context.output_dir)
    exp, run = create_simple_run(mlflow_context.client_src)
    run1 = mlflow_context.client_src.get_run(run.info.run_id)
    exporter.export_experiment(exp.name, mlflow_context.output_dir)

    experiment_name = create_dst_experiment_name(exp.name)
    importer.import_experiment(experiment_name, mlflow_context.output_dir)
    exp2 = mlflow_context.client_dst.get_experiment_by_name(experiment_name)
    infos = mlflow_context.client_dst.list_run_infos(exp2.experiment_id)
    run2 = mlflow_context.client_dst.get_run(infos[0].run_id)

    if verbose: dump_runs(run1, run2)
    return run1, run2

def test_exp_basic(mlflow_context):
    run1, run2 = init_exp_test(mlflow_context,
        ExperimentExporter(mlflow_context.client_src),
        ExperimentImporter(mlflow_context.client_dst), 
        True)
    compare_runs(mlflow_context.client_src, mlflow_context.output_dir, run1, run2)

def test_exp_import_metadata_tags(mlflow_context):
    run1, run2 = init_exp_test(mlflow_context,
       ExperimentExporter(mlflow_context.client_src, export_metadata_tags=True), 
       ExperimentImporter(mlflow_context.client_dst, import_metadata_tags=True), verbose=False)
    compare_run_import_metadata_tags(mlflow_context.client_src, mlflow_context.output_dir, run1, run2)
