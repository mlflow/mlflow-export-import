import os
from oss_utils_test import mk_test_object_name_default, list_experiments, delete_experiments_and_models
from compare_utils import compare_runs

from mlflow_export_import.bulk.export_models import export_models
from mlflow_export_import.bulk.import_models import import_all
from mlflow_export_import.bulk import bulk_utils
from test_bulk_experiments import create_test_experiment
from init_tests import mlflow_context

# == Setup

notebook_formats = "SOURCE,DBC"
num_models = 2
num_runs = 2

# == Compare

def compare_models(mlflow_context, compare_func):
    test_dir = os.path.join(mlflow_context.output_dir, "test_compare_runs")
    exps = list_experiments(mlflow_context.client_src)
    exp_ids = [ exp.experiment_id for exp in exps ]
    models2 = mlflow_context.client_dst.list_registered_models()
    assert len(models2) > 0
    for model2 in models2:
        versions2 = mlflow_context.client_dst.get_latest_versions(model2.name)
        for vr in versions2:
            run2 = mlflow_context.client_dst.get_run(vr.run_id)
            tag = run2.data.tags["my_uuid"]
            filter = f"tags.my_uuid = '{tag}'"
            run1 = mlflow_context.client_src.search_runs(exp_ids, filter)[0]
            tdir = os.path.join(test_dir,run2.info.run_id)
            os.makedirs(tdir)
            assert run1.info.run_id != run2.info.run_id
            compare_func(mlflow_context.client_src, mlflow_context.client_dst, run1, run2, tdir)

# == Export/import registered model tests

def create_model(client):
    exp = create_test_experiment(client, num_runs)
    model_name = mk_test_object_name_default()
    model = client.create_registered_model(model_name)
    for run in client.search_runs([exp.experiment_id]):
        source = f"{run.info.artifact_uri}/model"
        client.create_model_version(model_name, source, run.info.run_id)
    return model.name

def _run_test(mlflow_context, compare_func, use_threads=False):
    delete_experiments_and_models(mlflow_context)
    model_names = [ create_model(mlflow_context.client_src) for j in range(0,num_models) ]
    export_models(mlflow_context.client_src,
        model_names, 
        mlflow_context.output_dir, 
        notebook_formats, 
        stages="None", 
        export_all_runs=False, 
        use_threads=False)

    import_all(mlflow_context.client_dst,
        mlflow_context.output_dir,
        delete_model=False,
        use_src_user_id=False,
        verbose=False,
        use_threads=use_threads)

    compare_models(mlflow_context, compare_func)


def test_basic(mlflow_context):
    _run_test(mlflow_context, compare_runs)

def test_exp_basic_threads(mlflow_context):
    _run_test(mlflow_context, compare_runs, use_threads=True)

def test_exp_with_source_tags(mlflow_context):
    _run_test(mlflow_context, compare_runs)


def test_get_model_names_from_comma_delimited_string(mlflow_context):
    delete_experiments_and_models(mlflow_context)
    model_names = bulk_utils.get_model_names(mlflow_context.client_src,"model1,model2,model3")
    assert len(model_names) == 3

def test_get_model_names_from_all_string(mlflow_context):
    delete_experiments_and_models(mlflow_context)
    model_names1 = [ create_model(mlflow_context.client_src) for j in range(0,3) ]
    model_names2 = bulk_utils.get_model_names(mlflow_context.client_src, "*")
    assert set(model_names1) == set(model_names2)
