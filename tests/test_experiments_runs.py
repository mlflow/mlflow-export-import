from mlflow_export_import.run.export_run import RunExporter
from mlflow_export_import.run.import_run import RunImporter
from mlflow_export_import.experiment.export_experiment import ExperimentExporter
from mlflow_export_import.experiment.import_experiment import ExperimentImporter
from utils_test import create_simple_run, init_output_dirs
from compare_utils import compare_runs, compare_run_import_metadata_tags
from compare_utils import dump_runs
from init_tests import mlflow_server

# == Setup

mlmodel_fix = True

# == Export/import Run tests

def init_run_test(mlflow_server, exporter, importer, use_metric_steps=False, verbose=False):
    exp, run = create_simple_run(mlflow_server.client, use_metric_steps)
    exporter.export_run(run.info.run_id, mlflow_server.output_dir)

    experiment_name = f"{exp.name}_imported" 
    res = importer.import_run(experiment_name, mlflow_server.output_dir)
    if verbose: print("res:",res)

    run1 = mlflow_server.client.get_run(run.info.run_id)
    run2 = mlflow_server.client.get_run(res[0].info.run_id)
    if verbose: dump_runs(run1, run2)
    return run1, run2

def test_run_basic(mlflow_server):
    run1, run2 = init_run_test(mlflow_server, RunExporter(), RunImporter(mlmodel_fix=mlmodel_fix))
    compare_runs(mlflow_server.client, mlflow_server.output_dir, run1, run2)

def test_run_import_metadata_tags(mlflow_server):
    run1, run2 = init_run_test(mlflow_server, RunExporter(export_metadata_tags=True), RunImporter(mlmodel_fix=mlmodel_fix, import_metadata_tags=True), verbose=False)
    compare_run_import_metadata_tags(mlflow_server.client, mlflow_server.output_dir, run1, run2)

def test_run_basic_use_metric_steps(mlflow_server):
    run1, run2 = init_run_test(mlflow_server, RunExporter(), RunImporter(mlmodel_fix=mlmodel_fix), use_metric_steps=True)
    compare_runs(mlflow_server.client, mlflow_server.output_dir, run1, run2)

# == Export/import Experiment tests

def init_exp_test(mlflow_server, exporter, importer, verbose=False):
    init_output_dirs(mlflow_server.output_dir)
    exp, run = create_simple_run(mlflow_server.client)
    run1 = mlflow_server.client.get_run(run.info.run_id)
    exporter.export_experiment(exp.name, mlflow_server.output_dir)

    experiment_name = f"{exp.name}_imported"
    importer.import_experiment(experiment_name, mlflow_server.output_dir)
    exp2 = mlflow_server.client.get_experiment_by_name(experiment_name)
    infos = mlflow_server.client.list_run_infos(exp2.experiment_id)
    run2 = mlflow_server.client.get_run(infos[0].run_id)

    if verbose: dump_runs(run1, run2)
    return run1, run2

def test_exp_basic(mlflow_server):
    run1, run2 = init_exp_test(mlflow_server,ExperimentExporter(), ExperimentImporter(), True)
    compare_runs(mlflow_server.client, mlflow_server.output_dir, run1, run2)

def test_exp_import_metadata_tags(mlflow_server):
    run1, run2 = init_exp_test(mlflow_server,ExperimentExporter(export_metadata_tags=True), ExperimentImporter(import_metadata_tags=True), verbose=False)
    compare_run_import_metadata_tags(mlflow_server.client, mlflow_server.output_dir, run1, run2)
