from mlflow_export_import.experiment.export_experiment import ExperimentExporter
from mlflow_export_import.experiment.import_experiment import ExperimentImporter
from utils_test import create_simple_run, init_output_dirs, create_dst_experiment_name
from compare_utils import compare_runs, compare_runs_with_source_tags
from compare_utils import dump_runs
from init_tests import mlflow_context

# == Setup

mlmodel_fix = True

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
    compare_runs(mlflow_context.client_src, mlflow_context.client_dst, run1, run2, mlflow_context.output_dir)

def test_exp_with_source_tags(mlflow_context):
    run1, run2 = init_exp_test(mlflow_context,
       ExperimentExporter(mlflow_context.client_src, export_source_tags=True), 
       ExperimentImporter(mlflow_context.client_dst), verbose=False)
    compare_runs_with_source_tags(mlflow_context.client_src, mlflow_context.client_dst, run1, run2, mlflow_context.output_dir)
