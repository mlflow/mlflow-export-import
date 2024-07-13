from mlflow_export_import.bulk.export_all import export_all
from mlflow_export_import.bulk.import_models import import_models
from tests.open_source.test_bulk_experiments import compare_experiments
from tests.open_source.test_bulk_models import create_model, compare_models_with_versions, get_num_deleted_runs

from tests.open_source.init_tests import mlflow_context
from tests.compare_utils import compare_runs
from tests.open_source.oss_utils_test import delete_experiments_and_models

# == Helper functions

_notebook_formats = "SOURCE,DBC"
_num_models = 2
_num_runs = 2


def _run_test(mlflow_context, compare_func=compare_runs, use_threads=False):
    delete_experiments_and_models(mlflow_context)
    for _ in range( _num_models):
        create_model(mlflow_context.client_src)
    export_all(
        mlflow_client = mlflow_context.client_src,
        output_dir = mlflow_context.output_dir,
        notebook_formats = _notebook_formats,
        use_threads = use_threads
    )
    import_models(
        mlflow_client = mlflow_context.client_dst,
        input_dir = mlflow_context.output_dir,
        delete_model = True
    )
    compare_experiments(mlflow_context, compare_func)
    compare_models_with_versions(mlflow_context, compare_func)


# == Test basic

def test_basic(mlflow_context):
    _run_test(mlflow_context)


def test_basic_threads(mlflow_context):
    _run_test(mlflow_context, use_threads=True)


# == Test deleted runs

def test_model_deleted_runs(mlflow_context):
    model_name = create_model(mlflow_context.client_src)
    versions = mlflow_context.client_src.search_model_versions(filter_string=f"name='{model_name}'")
    assert len(versions) == _num_runs

    mlflow_context.client_src.delete_run(versions[0].run_id)
    num_deleted = get_num_deleted_runs(mlflow_context.client_src, versions)
    assert num_deleted == _num_runs - 1

    export_all(
        mlflow_client = mlflow_context.client_src,
        output_dir = mlflow_context.output_dir,
        export_deleted_runs = True
    )
    import_models(
        mlflow_client = mlflow_context.client_dst,
        input_dir = mlflow_context.output_dir,
        delete_model = True
    )
    versions = mlflow_context.client_dst.search_model_versions(filter_string=f"name='{model_name}'")
    assert len(versions) == _num_runs

    num_deleted2 = get_num_deleted_runs(mlflow_context.client_dst, versions)
    assert num_deleted == num_deleted2
