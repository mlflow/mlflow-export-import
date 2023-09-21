from mlflow_export_import.common.source_tags import ExportTags
from mlflow_export_import.copy import local_utils
from mlflow_export_import.copy import copy_model_version

from tests.open_source.init_tests import mlflow_context
from tests.open_source.oss_utils_test import create_experiment
from tests.open_source.oss_utils_test import mk_test_object_name_default
from tests.open_source.oss_utils_test import create_version
from tests.compare_utils import compare_runs


def test_with_experiment(mlflow_context):
    local_utils.dump_client(mlflow_context.client_src,"SRC CLIENT")
    local_utils.dump_client(mlflow_context.client_dst,"DST CLIENT")
    dst_exp = create_experiment(mlflow_context.client_src)
    vr, _ = _create_model_version(mlflow_context)
    dst_model_name = mk_test_object_name_default()

    src_vr, dst_vr = copy_model_version.copy(
        src_model_name = vr.name,
        src_model_version = vr.version,
        dst_model_name = dst_model_name,
        dst_experiment_name = dst_exp.name,
        src_tracking_uri = mlflow_context.client_src.tracking_uri,
        dst_tracking_uri = mlflow_context.client_dst.tracking_uri,
        verbose = False
    )
    assert vr == src_vr
    _compare_model_versions(src_vr, dst_vr)
    _compare_runs(mlflow_context, src_vr, dst_vr)

    assert src_vr.run_id != dst_vr.run_id
    assert dst_vr == mlflow_context.client_dst.get_model_version(dst_vr.name, dst_vr.version)


def test_without_experiment(mlflow_context):
    vr, _ = _create_model_version(mlflow_context)
    dst_model_name = mk_test_object_name_default()
    src_vr, dst_vr = copy_model_version.copy(
        src_model_name = vr.name,
        src_model_version = vr.version,
        dst_model_name = dst_model_name,
        dst_experiment_name = None,
        src_tracking_uri = mlflow_context.client_src.tracking_uri,
        dst_tracking_uri = mlflow_context.client_src.tracking_uri,
        verbose = False
    )
    assert vr == src_vr
    _compare_model_versions(src_vr, dst_vr)

    assert src_vr.run_id == dst_vr.run_id
    assert dst_vr == mlflow_context.client_src.get_model_version(dst_vr.name, dst_vr.version)


def test_with_experiment_and_copy_tags(mlflow_context):
    local_utils.dump_client(mlflow_context.client_src,"SRC CLIENT")
    local_utils.dump_client(mlflow_context.client_dst,"DST CLIENT")
    dst_exp = create_experiment(mlflow_context.client_src)
    vr, _ = _create_model_version(mlflow_context)
    dst_model_name = mk_test_object_name_default()

    src_vr, dst_vr = copy_model_version.copy(
        src_model_name = vr.name,
        src_model_version = vr.version,
        dst_model_name = dst_model_name,
        dst_experiment_name = dst_exp.name,
        src_tracking_uri = mlflow_context.client_src.tracking_uri,
        dst_tracking_uri = mlflow_context.client_dst.tracking_uri,
        add_copy_system_tags = True,
        verbose = False
    )
    _compare_model_versions(src_vr, dst_vr, True)
    _compare_runs(mlflow_context, src_vr, dst_vr)
    assert src_vr.run_id != dst_vr.run_id
    assert dst_vr == mlflow_context.client_dst.get_model_version(dst_vr.name, dst_vr.version)


def _compare_model_versions(src_vr, dst_vr, add_copy_system_tags=False):
    assert src_vr.description == dst_vr.description
    assert src_vr.aliases == dst_vr.aliases
    if add_copy_system_tags:
        src_tags = { k:v for k,v in src_vr.tags.items() if not k.startswith(ExportTags.PREFIX_ROOT) }
        dst_tags = { k:v for k,v in dst_vr.tags.items() if not k.startswith(ExportTags.PREFIX_ROOT) }
        assert src_tags == dst_tags
    else:
        assert src_vr.tags == dst_vr.tags

def _compare_runs(mlflow_context, src_vr, dst_vr):
    src_run = mlflow_context.client_src.get_run(src_vr.run_id)
    dst_run = mlflow_context.client_dst.get_run(dst_vr.run_id)
    compare_runs(mlflow_context, src_run, dst_run)

def _create_model_version(mlflow_context):
    model_name_src = mk_test_object_name_default()
    desc = "Hello decription"
    tags = { "city": "franconia" }
    mlflow_context.client_src.create_registered_model(model_name_src, tags, desc)
    return create_version(mlflow_context.client_src, model_name_src, "Production")
