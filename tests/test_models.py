import mlflow
from mlflow_export_import.model.export_model import ModelExporter
from mlflow_export_import.model.import_model import ModelImporter
from test_experiments_runs import create_simple_run
import utils_test 
from compare_utils import compare_runs

client = mlflow.tracking.MlflowClient()

output_dir = "out"

def test_export_import_model():
    run_src = _create_run()
    exporter = ModelExporter()
    model_name_src = f"model_{utils_test.mk_uuid()}"
    model_src = client.create_registered_model(model_name_src)
    source = f"{run_src.info.artifact_uri}/model"
    client.create_model_version(model_name_src, source, run_src.info.run_id)
    exporter.export_model(model_name_src, output_dir)

    model_name_dst = f"{model_name_src}_imported"
    experiment_name =  f"exp_{model_name_dst}"
    importer = ModelImporter()
    importer.import_model(model_name_dst, output_dir, experiment_name, delete_model=True, verbose=False, sleep_time=10)
    model_dst = client.get_registered_model(model_name_dst)

    model_src = client.get_registered_model(model_name_src)
    assert len(model_src.latest_versions) == len(model_dst.latest_versions)

    _compare_models(model_src, model_dst)
    _compare_version_lists(model_src.latest_versions, model_dst.latest_versions)


def test_export_import_model_stages():
    exporter = ModelExporter(stages=["Production","Staging"])
    model_name_src = f"model_{utils_test.mk_uuid()}"
    model_src = client.create_registered_model(model_name_src)

    _create_version(model_name_src, "Production")
    _create_version(model_name_src)
    vr_staging_src = _create_version(model_name_src, "Staging")
    vr_prod_src = _create_version(model_name_src, "Production")
    _create_version(model_name_src, "Archived")
    exporter.export_model(model_name_src, output_dir)

    model_name_dst = f"{model_name_src}_imported"
    experiment_name =  f"exp_{model_name_dst}"
    importer = ModelImporter()
    importer.import_model(model_name_dst, output_dir, experiment_name, delete_model=True, verbose=False, sleep_time=10)
    model_dst = client.get_registered_model(model_name_dst)

    model_dst = client.get_registered_model(model_name_dst)
    assert len(model_dst.latest_versions) == 2

    versions = client.get_latest_versions(model_name_dst)
    vr_prod_dst = [vr for vr in versions if vr.current_stage == "Production"][0]
    vr_staging_dst = [vr for vr in versions if vr.current_stage == "Staging"][0]

    _compare_models(model_src, model_dst)
    _compare_version_lists([vr_prod_src, vr_staging_src], [vr_prod_dst, vr_staging_dst])

def _create_version(model_name, stage=None):
    run = _create_run()
    source = f"{run.info.artifact_uri}/model"
    vr = client.create_model_version(model_name, source, run.info.run_id)
    if stage:
        vr = client.transition_model_version_stage(model_name, vr.version, stage)
    return vr

def _create_run():
    utils_test.create_output_dir(output_dir)
    _, run = create_simple_run()
    return client.get_run(run.info.run_id)
    
def _compare_models(model_src, model_dst):
    assert model_src.description == model_dst.description
    assert model_src.tags == model_dst.tags

def _compare_version_lists(versions_src, versions_dst):
    for (vr_src, vr_dst) in zip(versions_src, versions_dst):
        _compare_versions(vr_src, vr_dst)

def _compare_versions(vr_src, vr_dst):
    assert vr_src.current_stage == vr_dst.current_stage
    assert vr_src.description == vr_dst.description
    #assert vr_src.name == vr_dst.name # TODO: if in different tracking servers
    assert vr_src.status == vr_dst.status
    assert vr_src.status_message == vr_dst.status_message
    #assert vr_src.user_id == vr_dst.user_id # Only for open source MLflow
    assert vr_src.run_id != vr_dst.run_id
    run_src = client.get_run(vr_src.run_id)
    run_dst = client.get_run(vr_dst.run_id)
    compare_runs(client, output_dir, run_src, run_dst)


from mlflow_export_import.model.import_model import _extract_model_path

run_id = "48cf29167ddb4e098da780f0959fb4cf"
model_path = "models/my_model"

def test_extract_model_path_databricks():
    source = f"dbfs:/databricks/mlflow-tracking/4072937019901104/{run_id}/artifacts/{model_path}"
    _test_extract_model_path(source)

def test_extract_model_path_oss():
    source = f"/opt/mlflow_server/local_mlrun/mlruns/3/{run_id}/artifacts/{model_path}"
    _test_extract_model_path(source)

def _test_extract_model_path(source):
    model_path2 = _extract_model_path(source, run_id)
    assert model_path == model_path2
