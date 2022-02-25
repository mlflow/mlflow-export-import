import mlflow
from mlflow_export_import.run.export_run import RunExporter
from mlflow_export_import.run.import_run import RunImporter
from mlflow_export_import.experiment.export_experiment import ExperimentExporter
from mlflow_export_import.experiment.import_experiment import ExperimentImporter
from mlflow_export_import.run.copy_run import RunCopier
from mlflow_export_import.experiment.copy_experiment import ExperimentCopier
from utils_test import create_output_dir, create_simple_run, init_output_dirs, output_dir
from compare_utils import compare_runs, compare_run_no_import_mlflow_tags, compare_run_import_metadata_tags
from compare_utils import dump_runs

# == Setup

client = mlflow.tracking.MlflowClient()
#mlflow.sklearn.autolog()
mlmodel_fix = True

# == Export/import Run tests

def init_run_test(exporter, importer, verbose=False):
    create_output_dir()
    exp, run = create_simple_run()
    exporter.export_run(run.info.run_id, output_dir)

    experiment_name = f"{exp.name}_imported" 
    res = importer.import_run(experiment_name, output_dir)
    if verbose: print("res:",res)

    run1 = client.get_run(run.info.run_id)
    run2 = client.get_run(res[0].info.run_id)
    if verbose: dump_runs(run1, run2)
    return run1, run2

def test_run_basic():
    run1, run2 = init_run_test(RunExporter(), RunImporter(mlmodel_fix=mlmodel_fix, import_mlflow_tags=True))
    compare_runs(client, output_dir, run1, run2)

def test_run_no_import_mlflow_tags():
    run1, run2 = init_run_test(RunExporter(), RunImporter(mlmodel_fix=mlmodel_fix, import_mlflow_tags=False))
    compare_run_no_import_mlflow_tags(client, output_dir, run1, run2)

def test_run_import_metadata_tags():
    run1, run2 = init_run_test(RunExporter(export_metadata_tags=True), RunImporter(mlmodel_fix=mlmodel_fix, import_metadata_tags=True, import_mlflow_tags=True), verbose=False)
    compare_run_import_metadata_tags(client, output_dir, run1, run2)

# == Export/import Experiment tests

def init_exp_test(exporter, importer, verbose=False):
    init_output_dirs()
    exp, run = create_simple_run()
    run1 = client.get_run(run.info.run_id)
    exporter.export_experiment(exp.name, output_dir)

    experiment_name = f"{exp.name}_imported"
    importer.import_experiment(experiment_name, output_dir)
    exp2 = client.get_experiment_by_name(experiment_name)
    infos = client.list_run_infos(exp2.experiment_id)
    run2 = client.get_run(infos[0].run_id)

    if verbose: dump_runs(run1, run2)
    return run1, run2

def test_exp_basic():
    run1, run2 = init_exp_test(ExperimentExporter(), ExperimentImporter(), True)
    compare_runs(client, output_dir, run1, run2)

def test_exp_no_import_mlflow_tags():
    run1, run2 = init_exp_test(ExperimentExporter(), ExperimentImporter(import_mlflow_tags=False))
    compare_run_no_import_mlflow_tags(client, output_dir, run1, run2)

def test_exp_import_metadata_tags():
    run1, run2 = init_exp_test(ExperimentExporter(export_metadata_tags=True), ExperimentImporter(import_metadata_tags=True), verbose=False)
    compare_run_import_metadata_tags(client, output_dir, run1, run2)

# == Copy run tests

def init_run_copy_test(copier, verbose=False):
    init_output_dirs()
    exp, run = create_simple_run()
    run1 = client.get_run(run.info.run_id)
    dst_experiment_name = f"{exp.name}_copy_run"
    copier.copy_run(run1.info.run_id, dst_experiment_name)
    exp2 = client.get_experiment_by_name(dst_experiment_name)
    infos = client.list_run_infos(exp2.experiment_id)
    run2 = client.get_run(infos[0].run_id)
    if verbose: dump_runs(run1, run2)
    return run1, run2

def test_copy_run_basic():
    run1, run2 = init_run_copy_test(RunCopier(client, client), verbose=False)
    compare_runs(client, output_dir, run1, run2)

def test_copy_run_import_metadata_tags():
    run1, run2 = init_run_copy_test(RunCopier(client, client, export_metadata_tags=True))
    compare_run_import_metadata_tags(client, output_dir, run1, run2)

# == Copy experiment tests

def init_exp_copy_test(copier, verbose=False):
    init_output_dirs()
    exp, run = create_simple_run()
    run1 = client.get_run(run.info.run_id)
    dst_experiment_name = f"{exp.name}_copy_exp"
    copier.copy_experiment(exp.name, dst_experiment_name) # FAILS
    exp2 = client.get_experiment_by_name(dst_experiment_name)
    infos = client.list_run_infos(exp2.experiment_id)
    run2 = client.get_run(infos[0].run_id)
    if verbose: dump_runs(run1, run2)
    return run1, run2

def test_copy_exp_basic():
    init_exp_copy_test(ExperimentCopier(client, client), verbose=False)
    run1, run2 = init_exp_copy_test(ExperimentCopier(client, client), verbose=False)
    compare_runs(client, output_dir, run1, run2)

def test_copy_exp_import_metadata_tags():
    run1, run2 = init_exp_copy_test(ExperimentCopier(client, client, export_metadata_tags=True))
    compare_run_import_metadata_tags(client, output_dir, run1, run2)
