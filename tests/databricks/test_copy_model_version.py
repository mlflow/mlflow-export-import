from mlflow_export_import.copy import copy_model_version
from tests.core import to_MlflowContext
from tests.compare_utils import compare_versions
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
    compare_versions(to_MlflowContext(test_context), src_vr, dst_vr, False, False)
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
        copy_lineage_tags = True,
        verbose = True
    )
    assert src_vr == _src_vr
    test_context = local_utils.mk_one_workspace_test_context(test_context)
    compare_versions(to_MlflowContext(test_context), src_vr, dst_vr, False, False)
    assert src_vr.run_id != dst_vr.run_id
    assert dst_vr == test_context.mlflow_client_dst.get_model_version(dst_vr.name, dst_vr.version)


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
    test_context = local_utils.mk_one_workspace_test_context(test_context)
    compare_versions(to_MlflowContext(test_context), src_vr, dst_vr, False, True)
    assert src_vr.run_id == dst_vr.run_id
    assert dst_vr == test_context.mlflow_client_dst.get_model_version(dst_vr.name, dst_vr.version)
