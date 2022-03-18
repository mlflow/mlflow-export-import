import os
import mlflow
from utils_test import create_output_dir, output_dir, mk_uuid, delete_experiments
from compare_utils import compare_runs

from mlflow_export_import.model.export_model import ModelExporter
from mlflow_export_import.bulk.export_models import export_models
from mlflow_export_import.bulk.import_models import import_all
from mlflow_export_import.bulk import bulk_utils
from mlflow_export_import.common import model_utils
from test_bulk_experiments import create_test_experiment

# == Setup

notebook_formats = "SOURCE,DBC"
model_prefix = "Original"
num_models = 1
num_experiments = 1
exporter = ModelExporter() 
client = mlflow.tracking.MlflowClient()

def _init():
    create_output_dir()
    _delete_models()
    delete_experiments()

def _delete_models():
    for model in client.list_registered_models():
        model_utils.delete_model(client, model.name)

# == Export/import registered model tests

def _rename_model_name(model_name):
    return f"{model_prefix}_{model_name}"

def _create_model():
    exp = create_test_experiment(num_experiments)
    model_name = f"model_{mk_uuid()}"
    model = client.create_registered_model(model_name)
    for run in client.search_runs([exp.experiment_id]):
        source = f"{run.info.artifact_uri}/model"
        client.create_model_version(model_name, source, run.info.run_id)
    return model.name

def _run_test(compare_func, import_metadata_tags=False, use_threads=False):
    _init()
    model_names = [ _create_model() for j in range(0,num_models) ]
    export_models(model_names, output_dir, notebook_formats, stages="None", export_all_runs=False, use_threads=False)
    for model_name in model_names:
        client.rename_registered_model(model_name,_rename_model_name(model_name))
    exp_ids = [ exp.experiment_id for exp in client.list_experiments() ]
    exps = client.list_experiments() 
    for exp in exps:
        client.rename_experiment(exp.experiment_id, f"Original_{exp.name}")

    import_all(output_dir,
        delete_model=False,
        use_src_user_id=False,
        import_metadata_tags=import_metadata_tags,
        verbose=False,
        use_threads=use_threads)

    test_dir = os.path.join(output_dir,"test_compare_runs")
    os.makedirs(test_dir)

    models2 = client.search_registered_models("name like 'model_%'")
    for model2 in models2:
        model2 = client.get_registered_model(model2.name)
        versions = client.get_latest_versions(model2.name)
        for vr in versions:
            run2 = client.get_run(vr.run_id)
            tag = run2.data.tags["my_uuid"]
            filter = f"tags.my_uuid = '{tag}'"
            run1 = client.search_runs(exp_ids, filter)[0]
            tdir = os.path.join(test_dir,run2.info.run_id)
            os.makedirs(tdir)
            assert run1.info.run_id != run2.info.run_id
            compare_func(client, tdir, run1, run2)

def test_basic():
    _run_test(compare_runs)

def test_exp_basic_threads():
    _run_test(compare_runs, use_threads=True)

def test_exp_import_metadata_tags():
    _run_test(compare_runs, import_metadata_tags=True)


def test_get_model_names_from_comma_delimited_string():
    model_names = bulk_utils.get_model_names("model1,model2,model3")
    assert len(model_names) == 3

def test_get_model_names_from_all_string():
    _init()
    model_names1 = [ _create_model() for j in range(0,3) ]
    model_names2 = bulk_utils.get_model_names("*")
    assert set(model_names1) == set(model_names2)
