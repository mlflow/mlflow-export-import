from mlflow_export_import.copy import copy_model_version
from tests.core import to_MlflowContext, TestContext
from tests.compare_model_version_utils import compare_model_versions, compare_runs
from . init_tests import workspace_src, workspace_dst
from . import local_utils
from . init_tests import test_context


def test_two_workspaces(test_context):
    src_model_name = local_utils.mk_test_object_name_default()
    src_vr, _ = local_utils.create_version(test_context.mlflow_client_src, src_model_name, "Production")
    dst_exp_name = local_utils.mk_experiment_name(workspace=workspace_dst)
    _src_vr, dst_vr = copy_model_version.copy(
        src_model_name = src_vr.name,
        src_model_version = src_vr.version,
        dst_model_name = src_vr.name,
        dst_experiment_name = dst_exp_name,
        src_tracking_uri = workspace_src.cfg.profile,
        dst_tracking_uri = workspace_dst.cfg.profile,
        verbose = True
    )
    assert src_vr == _src_vr
    _compare_versions(test_context, src_vr, dst_vr)
    assert src_vr.run_id != dst_vr.run_id
    assert dst_vr == test_context.mlflow_client_dst.get_model_version(dst_vr.name, dst_vr.version)


def test_one_workspace_with_experiment(test_context):
    src_model_name = local_utils.mk_test_object_name_default()
    dst_model_name = local_utils.mk_test_object_name_default()
    src_vr, _ = local_utils.create_version(test_context.mlflow_client_src, src_model_name, "Production")
    dst_exp_name = local_utils.mk_experiment_name(workspace=workspace_dst)
    _src_vr, dst_vr = copy_model_version.copy(
        src_model_name = src_vr.name,
        src_model_version = src_vr.version,
        dst_model_name = dst_model_name,
        dst_experiment_name = dst_exp_name,
        src_tracking_uri = workspace_src.cfg.profile,
        dst_tracking_uri = workspace_src.cfg.profile,
        verbose = True
    )
    assert src_vr == _src_vr
    test_context2 = _mk_one_workspace_context(test_context)
    _compare_versions(test_context2, src_vr, dst_vr)
    assert src_vr.run_id != dst_vr.run_id
    assert dst_vr == test_context2.mlflow_client_dst.get_model_version(dst_vr.name, dst_vr.version)


def test_one_workspace_without_experiment(test_context):
    src_model_name = local_utils.mk_test_object_name_default()
    dst_model_name = local_utils.mk_test_object_name_default()
    src_vr, _ = local_utils.create_version(test_context.mlflow_client_src, src_model_name, "Production")
    _src_vr, dst_vr = copy_model_version.copy(
        src_model_name = src_vr.name,
        src_model_version = src_vr.version,
        dst_model_name = dst_model_name,
        dst_experiment_name = None,
        src_tracking_uri = workspace_src.cfg.profile,
        dst_tracking_uri = workspace_src.cfg.profile,
        verbose = True
    )
    assert src_vr == _src_vr
    test_context2 = _mk_one_workspace_context(test_context)
    _compare_versions(test_context2, src_vr, dst_vr)
    assert src_vr.run_id == dst_vr.run_id
    assert dst_vr == test_context2.mlflow_client_dst.get_model_version(dst_vr.name, dst_vr.version)


def _compare_versions(test_context, src_vr, dst_vr):
    mlflow_context = to_MlflowContext(test_context)
    compare_model_versions(src_vr, dst_vr)
    compare_runs(mlflow_context, src_vr, dst_vr)

def _mk_one_workspace_context(test_context):
    return TestContext(
        test_context.mlflow_client_src,
        test_context.mlflow_client_src,
        test_context.dbx_client_src,
        test_context.dbx_client_src,
        test_context.output_dir,
        test_context.output_run_dir
    )
