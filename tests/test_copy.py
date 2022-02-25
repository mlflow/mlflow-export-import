import mlflow
from mlflow_export_import.run.copy_run import RunCopier
from mlflow_export_import.experiment.copy_experiment import ExperimentCopier
from compare_utils import compare_runs, compare_run_import_metadata_tags
from compare_utils import dump_runs
from utils_test import init_output_dirs, create_simple_run, output_dir

# == Setup

client = mlflow.tracking.MlflowClient()

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
