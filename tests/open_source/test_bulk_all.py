from test_bulk_experiments import compare_experiments
from test_bulk_models import create_model, compare_models_with_versions
from init_tests import mlflow_context
from mlflow_export_import.bulk.export_all import export_all
from mlflow_export_import.bulk.import_models import import_all
from oss_utils_test import delete_experiments_and_models
from compare_utils import compare_runs

notebook_formats = "SOURCE,DBC"
num_models = 2
num_runs = 3


def _run_test(mlflow_context, compare_func, use_threads=False):
    delete_experiments_and_models(mlflow_context)
    for _ in range(0,num_models):
        create_model(mlflow_context.client_src) 
    export_all(mlflow_context.output_dir, notebook_formats=notebook_formats, use_threads=use_threads)
    import_all(mlflow_context.client_dst, mlflow_context.output_dir, delete_model=True)
    compare_experiments(mlflow_context, compare_func)
    compare_models_with_versions(mlflow_context, compare_func)

def test_basic(mlflow_context):
    _run_test(mlflow_context, compare_runs)

def test_exp_basic_threads(mlflow_context):
    _run_test(mlflow_context, compare_runs, use_threads=True)

#def test_exp_with_source_tags(mlflow_context): # TODO
    #_run_test(mlflow_context, compare_runs, export_source_tags=True)

#def test_exp_with_source_tags_threads(mlflow_context): # TODO
    #_run_test(mlflow_context, compare_runs, export_source_tags=True, use_threads=True)
