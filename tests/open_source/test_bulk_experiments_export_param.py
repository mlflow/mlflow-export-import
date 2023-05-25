
"""
test parameter 'experiments' in export_experiments() from bulk/export_experiments.py

   :param experiments: Can be either:
      - File (ending with '.txt') containing list of experiment names or IDS
      - List of experiment names
      - List of experiment IDs
      - Dictionary whose key is an experiment id and the value is a list of run IDs
      - Dictionary whose key is an experiment id and the value is a list of its run IDs
      - String with comma-delimited experiment names or IDs such as 'sklearn_wine,sklearn_iris' or '1,2'
"""

from mlflow_export_import.bulk.export_experiments import export_experiments
from mlflow_export_import.bulk.import_experiments import import_experiments

from tests.open_source.init_tests import mlflow_context
from tests.open_source.oss_utils_test import delete_experiments_and_models
from tests.open_source.test_bulk_experiments import compare_experiments, _create_test_experiment

# == Export/import Experiments tests

def _run_test(mlflow_context, experiment_input_arg):
    export_experiments(
        mlflow_client = mlflow_context.client_src,
        experiments = experiment_input_arg,
        output_dir = mlflow_context.output_dir)
    import_experiments(
        mlflow_client = mlflow_context.client_dst,
        input_dir = mlflow_context.output_dir)
    compare_experiments(mlflow_context)

def _create_experiments(mlflow_context):
    delete_experiments_and_models(mlflow_context)
    exps = [ _create_test_experiment(mlflow_context.client_src, 2), _create_test_experiment(mlflow_context.client_src, 2) ]
    return exps


def test_experiment_names(mlflow_context):
    exps = _create_experiments(mlflow_context)
    exp_names = [ exp.name for exp in exps ]
    _run_test(mlflow_context, exp_names)

def test_experiment_ids(mlflow_context):
    exps = _create_experiments(mlflow_context)
    exp_ids = [ exp.experiment_id for exp in exps ]
    _run_test(mlflow_context, exp_ids)


def test_experiment_names_string(mlflow_context):
    exps = _create_experiments(mlflow_context)
    exp_names = [ exp.name for exp in exps ]
    _run_test(mlflow_context, ",".join(exp_names))

def test_experiment_ids_string(mlflow_context):
    exps = _create_experiments(mlflow_context)
    exp_ids = [ exp.experiment_id for exp in exps ]
    _run_test(mlflow_context, ",".join(exp_ids))


def _run_test_experiment_runs_file(mlflow_context, use_experiment_id):
    import tempfile
    exps = _create_experiments(mlflow_context)
    with tempfile.NamedTemporaryFile(suffix=".txt", mode="w") as f:
        for exp in exps:
            if use_experiment_id:
                f.file.write(exp.experiment_id+"\n")
            else:
                f.file.write(exp.name+"\n")
        f.file.close()
        _run_test(mlflow_context, f.name)

def test_experiment_runs_file_experiment_id(mlflow_context):
    _run_test_experiment_runs_file(mlflow_context, use_experiment_id=True)

def test_experiment_runs_file_experiment_name(mlflow_context):
    _run_test_experiment_runs_file(mlflow_context, use_experiment_id=False)


def test_experiment_runs_map(mlflow_context):
    exps = _create_experiments(mlflow_context)
    exp_runs_dct = {}
    for exp in exps:
        runs = mlflow_context.client_src.search_runs(exp.experiment_id)
        exp_runs_dct[exp.experiment_id] = [ run.info.run_id for run in runs ]
    _run_test(mlflow_context, exp_runs_dct)
