"""
Compare MLflow object utilities.
"""

from mlflow_export_import.common import utils, model_utils
from mlflow_export_import.common.source_tags import ExportTags
from mlflow_export_import.common.model_utils import is_unity_catalog_model
from tests import utils_test


def compare_runs(mlflow_context, run1, run2, import_source_tags=False, output_dir=None):
    output_dir = output_dir or mlflow_context.output_dir
    if import_source_tags:
        _compare_runs_with_source_tags(run1, run2)
    else:
        _compare_runs_without_source_tags(mlflow_context, run1, run2, output_dir)


def _compare_runs_without_source_tags(mlflow_context, run1, run2, output_dir):
    _compare_runs_common(run1, run2)
    _compare_common_tags(run1, run2)
    _compare_runs_without_tags(mlflow_context, run1, run2, output_dir)


def _compare_runs_with_source_tags(run1, run2):
    _compare_runs_common(run1, run2)
    source_tags2 = _strip_mlflow_export_import_tags(run2.data.tags)
    assert len(source_tags2) > 0, f"Source tags starting with '{ExportTags.PREFIX_ROOT}' are missing"


def _compare_runs_common(run1, run2):
    assert run1.data.params == run2.data.params
    assert run1.data.metrics == run2.data.metrics
    assert run1.inputs == run2.inputs


def compare_experiment_tags(tags1, tags2, import_source_tags=False):
    if not import_source_tags:
        assert tags1 == tags2
        return

    source_tags2 = { k:v for k,v in tags2.items() if k.startswith(ExportTags.PREFIX_MLFLOW_TAG) }
    mlflow_tags1 = { k:v for k,v in tags1.items() if k.startswith("mlflow.") }
    mlflow_tags2 = { k.replace(f"{ExportTags.PREFIX_MLFLOW_TAG}.","mlflow."):v for k,v in source_tags2.items() }
    assert mlflow_tags1 == mlflow_tags2

    tags2_no_source_tags = _strip_mlflow_export_import_tags(tags2)
    assert tags1 == tags2_no_source_tags


def _compare_common_tags(run1, run2):
    tags1 = { k:v for k,v in run1.data.tags.items() if not k.startswith("mlflow") }
    tags2 = { k:v for k,v in run2.data.tags.items() if not k.startswith("mlflow") }
    assert tags1 == tags2


def _compare_runs_without_tags(mlflow_context, run1, run2, output_dir):
    run_artifact_dir1, run_artifact_dir2 = utils_test.create_run_artifact_dirs(output_dir)
    _compare_run_info(run1, run2)
    _compare_data(run1, run2)
    _compare_artifacts(mlflow_context, run1, run2, run_artifact_dir1, run_artifact_dir2)


def _compare_run_info(run1, run2):
    assert run1.info.lifecycle_stage == run2.info.lifecycle_stage
    assert run1.info.status == run2.info.status


def _compare_data(run1, run2):
    assert run1.data.params == run2.data.params
    assert run1.data.metrics == run2.data.metrics
    _compare_common_tags(run1, run2)


def _compare_artifacts(mlflow_context, run1, run2, run_artifact_dir1, run_artifact_dir2):
    path1 = mlflow_context.client_src.download_artifacts(run1.info.run_id, ".", dst_path=run_artifact_dir1)
    path2 = mlflow_context.client_dst.download_artifacts(run2.info.run_id, ".", dst_path=run_artifact_dir2)
    assert utils_test.compare_dirs(path1, path2)


def compare_models(model_src, model_dst, compare_names):
    if compare_names:
        assert model_src.name == model_dst.name
    else:
        assert model_src.name != model_dst.name # When testing against Databricks, for now we use one tracking server and thus the model names are different
    assert model_src.description == model_dst.description
    assert model_src.tags.items() <= model_dst.tags.items()


def compare_models_with_versions(mlflow_context, model_src, model_dst, compare_names=None):
    if compare_names is None:
        compare_names = mlflow_context.client_src != mlflow_context.client_dst
    compare_models(model_src, model_dst, compare_names)
    if not is_unity_catalog_model(model_src.name) and not is_unity_catalog_model(model_dst.name):
        for (vr_src, vr_dst) in zip(model_src.latest_versions, model_dst.latest_versions):
            compare_versions(mlflow_context, vr_src, vr_dst, compare_names)
    vrs_src = model_utils.search_model_versions(mlflow_context.client_src, f"name='{model_src.name}'")
    vrs_dst = model_utils.search_model_versions(mlflow_context.client_dst, f"name='{model_dst.name}'")
    vrs_src = { vr.tags["uuid"]:vr for vr in vrs_src }
    for vr_dst in vrs_dst:
        vr_src = vrs_src.get(vr_dst.tags["uuid"])
        assert vr_src
        compare_versions(mlflow_context, vr_src, vr_dst, compare_names)


def compare_versions(mlflow_context, vr_src, vr_dst, compare_names=True, run_ids_equal=False):
    assert vr_src.current_stage == vr_dst.current_stage
    assert vr_src.description == vr_dst.description
    assert vr_src.status == vr_dst.status
    assert vr_src.status_message == vr_dst.status_message
    assert vr_src.aliases == vr_dst.aliases
    if compare_names and mlflow_context.client_src != mlflow_context.client_dst:
        assert vr_src.name == vr_dst.name
    if not utils.importing_into_databricks():
        assert vr_src.user_id == vr_dst.user_id

    src_tags = _strip_mlflow_export_import_tags(vr_src.tags)
    dst_tags = _strip_mlflow_export_import_tags(vr_dst.tags)
    assert src_tags == dst_tags

    if run_ids_equal:
        assert vr_src.run_id == vr_dst.run_id
    else:
        assert vr_src.run_id != vr_dst.run_id

    run_src = mlflow_context.client_src.get_run(vr_src.run_id)
    run_dst = mlflow_context.client_dst.get_run(vr_dst.run_id)
    compare_runs(mlflow_context, run_src, run_dst)


def _strip_mlflow_export_import_tags(tags):
    return { k:v for k,v in tags.items() if not k.startswith(ExportTags.PREFIX_ROOT) }
