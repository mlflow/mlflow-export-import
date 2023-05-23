"""
Compare MLflow object utilities.
"""

from mlflow_export_import.common import utils
from mlflow_export_import.common.source_tags import ExportTags
from tests import utils_test

def compare_runs(mlflow_context, run1, run2, import_source_tags=False, output_dir=None):
    output_dir = output_dir or mlflow_context.output_dir
    if import_source_tags:
        _compare_runs_with_source_tags(run1, run2)
    else:
        _compare_runs_without_source_tags(mlflow_context, run1, run2, output_dir)


def _compare_runs_without_source_tags(mlflow_context, run1, run2, output_dir):
    _compare_common_tags(run1, run2)
    _compare_runs_without_tags(mlflow_context, run1, run2, output_dir)


def _compare_runs_with_source_tags(run1, run2):
    assert run1.data.params == run2.data.params
    assert run1.data.metrics == run2.data.metrics
    source_tags2 = { k:v for k,v in run2.data.tags.items() if k.startswith(ExportTags.PREFIX_ROOT) }
    assert len(source_tags2) > 0, f"Source tags starting with '{ExportTags.PREFIX_ROOT}' are missing"
    for k,v in utils.strip_underscores(run1.info).items():
        if k != "run_name":
            assert str(v) == source_tags2[f"{ExportTags.PREFIX_RUN_INFO}.{k}"],f"Assert failed for RunInfo field '{k}'" # NOTE: tag values must be strings

def compare_experiment_tags(tags1, tags2, import_source_tags=False):
    if not import_source_tags:
        assert tags1 == tags2
        return

    source_tags2 = { k:v for k,v in tags2.items() if k.startswith(ExportTags.PREFIX_MLFLOW_TAG) }
    mlflow_tags1 = { k:v for k,v in tags1.items() if k.startswith("mlflow.") }
    mlflow_tags2 = { k.replace(f"{ExportTags.PREFIX_MLFLOW_TAG}.","mlflow."):v for k,v in source_tags2.items() }
    assert mlflow_tags1 == mlflow_tags2

    tags2_no_source_tags = { k:v for k,v in tags2.items() if not k.startswith(ExportTags.PREFIX_ROOT) }
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


def compare_models(model_src, model_dst, compare_name):
    if compare_name:
        assert model_src.name == model_dst.name
    else:
        assert model_src.name != model_dst.name # When testing against Databricks, for now we use one tracking server and thus the model names are different
    assert model_src.description == model_dst.description
    assert model_src.tags.items() <= model_dst.tags.items()


def compare_models_with_versions(mlflow_context, model_src, model_dst):
    compare_models(model_src, model_dst, mlflow_context.client_src!=mlflow_context.client_dst)
    for (vr_src, vr_dst) in zip(model_src.latest_versions, model_dst.latest_versions):
        compare_versions(mlflow_context, vr_src, vr_dst)


def compare_versions(mlflow_context, vr_src, vr_dst):
    assert vr_src.current_stage == vr_dst.current_stage
    assert vr_src.description == vr_dst.description
    assert vr_src.status == vr_dst.status
    assert vr_src.status_message == vr_dst.status_message
    if mlflow_context.client_src != mlflow_context.client_dst:
        assert vr_src.name == vr_dst.name
    if not utils.importing_into_databricks():
        assert vr_src.user_id == vr_dst.user_id

    tags_dst = { k:v for k,v in vr_dst.tags.items() if not k.startswith(ExportTags.PREFIX_ROOT) }
    assert vr_src.tags == tags_dst

    assert vr_src.run_id != vr_dst.run_id
    run_src = mlflow_context.client_src.get_run(vr_src.run_id)
    run_dst = mlflow_context.client_dst.get_run(vr_dst.run_id)
    compare_runs(mlflow_context, run_src, run_dst)


def dump_runs(run1, run2):
    from mlflow_export_import.common.dump_run import dump_run
    print("======= Run1")
    dump_run(run1)
    print("======= Run2")
    dump_run(run2)
