import os
from mlflow_export_import.common.source_tags import ExportTags
from mlflow_export_import.common import MlflowExportImportException
from mlflow_export_import.common.model_utils import model_names_same_registry
from mlflow_export_import.model.export_model import export_model
from mlflow_export_import.model.import_model import import_model
from mlflow_export_import.model.import_model import _extract_model_path, _path_join

from tests.open_source.oss_utils_test import create_simple_run, create_version
from tests.open_source.oss_utils_test import mk_test_object_name_default, mk_dst_model_name
from tests.compare_utils import compare_models_with_versions, compare_models, compare_versions
from tests.open_source.init_tests import mlflow_context


# == Test stages

def test_export_import_model_1_stage(mlflow_context):
    model_src, model_dst = _run_test_export_import_model_stages(mlflow_context, stages=["Production"] )
    assert len(model_dst.latest_versions) == 1
    compare_models_with_versions(mlflow_context, model_src, model_dst)


def test_export_import_model_2_stages(mlflow_context):
    model_src, model_dst = _run_test_export_import_model_stages(mlflow_context, stages=["Production","Staging"])
    assert len(model_dst.latest_versions) == 2
    compare_models_with_versions(mlflow_context, model_src, model_dst)


def test_export_import_model_all_stages(mlflow_context):
    model_src, model_dst = _run_test_export_import_model_stages(mlflow_context, stages=None)
    assert len(model_dst.latest_versions) == 4
    compare_models_with_versions(mlflow_context, model_src, model_dst)


# == Test stages and versions

def test_export_import_model_both_stages(mlflow_context):
    try:
        _run_test_export_import_model_stages(mlflow_context,  stages=["Production"], versions=[1])
    except MlflowExportImportException:
        # "Both stages {self.stages} and versions {self.versions} cannot be set")
        pass


# == Test versions

def _get_version_ids(model):
    return [vr.version for vr in model.latest_versions ]


def _get_version_ids_dst(model):
    return [vr.tags[f"{ExportTags.PREFIX_FIELD}.version"] for vr in model.latest_versions ]


def test_export_import_model_first_two_versions(mlflow_context):
    model_src, model_dst = _run_test_export_import_model_stages(mlflow_context, versions=["1","2"])
    assert len(model_dst.latest_versions) == 2
    compare_models_with_versions(mlflow_context, model_src, model_dst)
    ids_src = _get_version_ids(model_src)
    ids_dst = _get_version_ids(model_dst)
    for j, id in enumerate(ids_dst):
        assert(id == ids_src[j])


def test_export_import_model_two_from_middle_versions(mlflow_context):
    model_src, model_dst = _run_test_export_import_model_stages(mlflow_context, versions=["2","3","4"])
    assert len(model_dst.latest_versions) == 3
    ids_src = _get_version_ids(model_src)
    ids_dst = _get_version_ids_dst(model_dst)
    assert set(ids_dst).issubset(set(ids_src))

    compare_models(model_src, model_dst, mlflow_context.client_src!=mlflow_context.client_dst)
    for vr_dst in model_dst.latest_versions:
        vr_src_id = vr_dst.tags[f"{ExportTags.PREFIX_FIELD}.version"]
        vr_src = [vr for vr in model_src.latest_versions if vr.version == vr_src_id ]
        assert(len(vr_src)) == 1
        vr_src = vr_src[0]
        assert(vr_src.version == vr_src_id)
        compare_versions(mlflow_context, vr_src, vr_dst)

# == Test export deleted runs

def _run_test_deleted_runs(mlflow_context, delete_run, export_deleted_runs):
    model_name_src = mk_test_object_name_default()
    mlflow_context.client_src.create_registered_model(model_name_src)

    create_version(mlflow_context.client_src, model_name_src, "Production")
    _, run2 = create_version(mlflow_context.client_src, model_name_src, "Staging")
    versions = mlflow_context.client_src.search_model_versions(filter_string=f"name='{model_name_src}'")
    if delete_run:
        mlflow_context.client_src.delete_run(run2.info.run_id)
    run2 = mlflow_context.client_src.get_run(run2.info.run_id)

    export_model(
        model_name = model_name_src,
        output_dir = mlflow_context.output_dir,
        export_deleted_runs = export_deleted_runs,
        mlflow_client = mlflow_context.client_src
    )
    model_name_dst = mk_dst_model_name(model_name_src)
    import_model(
        model_name = model_name_dst,
        experiment_name = model_name_dst,
        input_dir = mlflow_context.output_dir,
        mlflow_client = mlflow_context.client_dst
    )
    versions = mlflow_context.client_dst.search_model_versions(filter_string=f"name='{model_name_dst}'")
    run_lifecycle_stages =  [ mlflow_context.client_dst.get_run(vr.run_id).info.lifecycle_stage for vr in versions ]
    return versions, run_lifecycle_stages


def test_export_delete_Yes_delete_run_No(mlflow_context):
    " Test: export-deleted-runs==Yes and no run deleted "
    versions, run_lifecycle_stages  = _run_test_deleted_runs(mlflow_context, False, True)
    assert len(versions) == 2
    assert run_lifecycle_stages == ["active", "active"]


def test_export_delete_Yes_delete_run_Yes(mlflow_context):
    " Test: export-deleted-runs==True and run deleted "
    versions, run_lifecycle_stages = _run_test_deleted_runs(mlflow_context, True, True)
    assert len(versions) == 2
    assert run_lifecycle_stages == ["deleted", "active"]


def test_export_delete_No_delete_run_Yes(mlflow_context):
    " Test: export-deleted-runs==False and no run deleted "
    versions, run_lifecycle_stages = _run_test_deleted_runs(mlflow_context, True, False)
    assert len(versions) == 1
    assert run_lifecycle_stages == ["active"]


# == Internal

def _run_test_export_import_model_stages(mlflow_context, stages=None, versions=None):
    model_name_src = mk_test_object_name_default()
    desc = "Hello decription"
    tags = { "city": "franconia" }
    model_src = mlflow_context.client_src.create_registered_model(model_name_src, tags, desc)

    create_version(mlflow_context.client_src, model_name_src, "Production")
    create_version(mlflow_context.client_src, model_name_src, "Staging")
    create_version(mlflow_context.client_src, model_name_src, "Archived")
    create_version(mlflow_context.client_src, model_name_src, "None")

    model_src = mlflow_context.client_src.get_registered_model(model_name_src)
    export_model(
        model_name = model_name_src,
        output_dir = mlflow_context.output_dir,
        stages = stages,
        versions = versions,
        mlflow_client = mlflow_context.client_src
    )

    model_name_dst = mk_dst_model_name(model_name_src)
    import_model(
        model_name = model_name_dst,
        experiment_name = model_name_dst,
        input_dir = mlflow_context.output_dir,
        import_source_tags = True,
        delete_model = True,
        mlflow_client = mlflow_context.client_dst
    )

    model_dst = mlflow_context.client_dst.get_registered_model(model_name_dst)
    return model_src, model_dst


def _create_run(client):
    _, run = create_simple_run(client)
    return client.get_run(run.info.run_id)


# == Test parsing for _extract_model_path to extract from version `source` field

_exp_id = "1812"
_run_id = "48cf29167ddb4e098da780f0959fb4cf"
_local_path_base = os.path.join("dbfs:/databricks/mlflow-tracking", _exp_id, _run_id)
_mlflow_artifacts_path_base = os.path.join("mlflow-artifacts:", _exp_id, _run_id)


def test_extract_no_artifacts():
    source = os.path.join(_local_path_base)
    model_path = _extract_model_path(source, _run_id)
    assert model_path == ""


def test_extract_just_artifacts():
    source = os.path.join(_local_path_base, "artifacts")
    model_path = _extract_model_path(source, _run_id)
    assert model_path == ""


def test_extract_just_artifacts_slash():
    source = os.path.join(_local_path_base, "artifacts/")
    model_path = _extract_model_path(source, _run_id)
    assert model_path == ""


def test_extract_model():
    source = os.path.join(_local_path_base, "artifacts","model")
    model_path = _extract_model_path(source, _run_id)
    assert model_path == "model"


def test_extract_model_sklearn():
    source = os.path.join(_local_path_base, "artifacts","model/sklearn")
    model_path = _extract_model_path(source, _run_id)
    assert model_path == "model/sklearn"


def test_extract_no_run_id():
    source = os.path.join(_local_path_base, "artifacts")
    try:
        _extract_model_path(source, "1215")
        assert False
    except MlflowExportImportException:
        pass

def test_mlflow_artifacts_path_no_artifacts():
    source = os.path.join(_mlflow_artifacts_path_base)
    model_path = _extract_model_path(source, _run_id)
    assert model_path == ""

def test_mlflow_artifacts_path_extract_model():
    source = os.path.join(_mlflow_artifacts_path_base, "model")
    model_path = _extract_model_path(source, _run_id)
    assert model_path == "model"

# == Test that both model names are either UC model names or WS model names

def test_both_model_names_are_uc():
    assert model_names_same_registry("model1", "model2")

def test_both_model_names_are_ws():
    assert model_names_same_registry("andre.models.model1", "andre.models.model2")

def test_both_model_names_are_not_same_1():
    assert not model_names_same_registry("model1", "andre.models.model2")

def test_both_model_names_are_not_same_2():
    assert not model_names_same_registry("andre.models.model2", "model1")


# == Test for DOS path adjustment

_base_dir = "dbfs:/mlflow/1812"
_expected_path = "dbfs:/mlflow/1812/model"

def test_path_join_frontslash():
    res = _path_join(_base_dir, "model")
    assert res == os.path.join(_expected_path)

def test_path_join_backslash():
    dir = _base_dir.replace("/","\\")
    res = _path_join(dir, "model")
    assert res == os.path.join(_expected_path)
