from mlflow_export_import.copy import copy_model_version
from mlflow_export_import.common import dump_utils

from tests.core import to_MlflowContext
from tests.compare_utils import compare_versions
from tests.databricks.init_tests import workspace_src, workspace_dst
from tests.databricks.init_tests import test_context
from tests.databricks import local_utils


def test_two_workspaces(test_context):
    src_model_name = local_utils.mk_uc_model_name(workspace_src)
    src_vr, _ = local_utils.create_version(test_context.mlflow_client_src, src_model_name)
    dump_utils.dump_obj(src_vr, "SRC Version")
    dst_model_name = local_utils.mk_uc_model_name(workspace_dst)
    dst_exp_name = local_utils.mk_experiment_name(workspace_dst)

    _src_vr, dst_vr = copy_model_version.copy(
        src_model_name = src_vr.name,
        src_model_version = src_vr.version,
        dst_model_name = dst_model_name,
        dst_experiment_name = dst_exp_name,
        src_tracking_uri = workspace_src.mlflow_client.tracking_uri,
        dst_tracking_uri = workspace_dst.mlflow_client.tracking_uri,
        src_registry_uri = workspace_src.mlflow_client._registry_uri,
        dst_registry_uri = workspace_dst.mlflow_client._registry_uri,
        verbose = True
    )
    dump_utils.dump_obj(dst_vr, "DST Version")
    assert src_vr == _src_vr
    _compare_versions(test_context, src_vr, dst_vr, False)
    assert src_vr.run_id != dst_vr.run_id
    assert dst_vr == test_context.mlflow_client_dst.get_model_version(dst_vr.name, dst_vr.version)


def test_one_workspace_with_experiment(test_context):
    src_model_name = local_utils.mk_uc_model_name(workspace_src)
    src_vr, _ = local_utils.create_version(test_context.mlflow_client_src, src_model_name)
    dump_utils.dump_obj(src_vr, "SRC Version")
    dst_model_name = local_utils.mk_uc_model_name(workspace_src)
    dst_exp_name = local_utils.mk_experiment_name(workspace_src)

    _src_vr, dst_vr = copy_model_version.copy(
        src_model_name = src_vr.name,
        src_model_version = src_vr.version,
        dst_model_name = dst_model_name,
        dst_experiment_name = dst_exp_name,
        src_tracking_uri = workspace_src.mlflow_client.tracking_uri,
        dst_tracking_uri = workspace_src.mlflow_client.tracking_uri,
        src_registry_uri = workspace_src.mlflow_client._registry_uri,
        dst_registry_uri = workspace_src.mlflow_client._registry_uri,
        verbose = True
    )
    dump_utils.dump_obj(dst_vr, "DST Version")
    assert src_vr == _src_vr
    test_context2 = local_utils.mk_one_workspace_test_context(test_context)
    _compare_versions(test_context2, src_vr, dst_vr, False)
    assert src_vr.run_id != dst_vr.run_id
    assert dst_vr == test_context2.mlflow_client_dst.get_model_version(dst_vr.name, dst_vr.version)


def test_one_workspace_without_experiment(test_context):
    src_model_name = local_utils.mk_uc_model_name(workspace_src)
    src_vr, _ = local_utils.create_version(test_context.mlflow_client_src, src_model_name)
    dump_utils.dump_obj(src_vr, "SRC Version")
    dst_model_name = local_utils.mk_uc_model_name(workspace_src)

    _src_vr, dst_vr = copy_model_version.copy(
        src_model_name = src_vr.name,
        src_model_version = src_vr.version,
        dst_model_name = dst_model_name,
        dst_experiment_name = None,
        src_tracking_uri = workspace_src.mlflow_client.tracking_uri,
        dst_tracking_uri = workspace_src.mlflow_client.tracking_uri,
        src_registry_uri = workspace_src.mlflow_client._registry_uri,
        dst_registry_uri = workspace_src.mlflow_client._registry_uri,
        verbose = True
    )
    dump_utils.dump_obj(dst_vr, "DST Version")
    assert src_vr == _src_vr
    test_context2 = local_utils.mk_one_workspace_test_context(test_context)
    _compare_versions(test_context2, src_vr, dst_vr, True)
    assert src_vr.run_id == dst_vr.run_id
    assert dst_vr == test_context2.mlflow_client_dst.get_model_version(dst_vr.name, dst_vr.version)


def test_two_workspaces_stages_aliases(test_context):
    src_model_name = local_utils.mk_uc_model_name(workspace_src)
    src_vr, _ = local_utils.create_version(test_context.mlflow_client_src, src_model_name)
    dump_utils.dump_obj(src_vr, "SRC Version")
    dst_model_name = local_utils.mk_uc_model_name(workspace_dst)
    dst_exp_name = local_utils.mk_experiment_name(workspace_dst)

    _src_vr, dst_vr = copy_model_version.copy(
        src_model_name = src_vr.name,
        src_model_version = src_vr.version,
        dst_model_name = dst_model_name,
        dst_experiment_name = dst_exp_name,
        src_tracking_uri = workspace_src.mlflow_client.tracking_uri,
        dst_tracking_uri = workspace_dst.mlflow_client.tracking_uri,
        src_registry_uri = workspace_src.mlflow_client._registry_uri,
        dst_registry_uri = workspace_dst.mlflow_client._registry_uri,
        copy_stages_and_aliases = True,
        verbose = True
    )
    dump_utils.dump_obj(dst_vr, "DST Version")
    assert src_vr == _src_vr
    _compare_versions(test_context, src_vr, dst_vr, False, compare_stages=True)
    assert src_vr.run_id != dst_vr.run_id
    assert dst_vr == test_context.mlflow_client_dst.get_model_version(dst_vr.name, dst_vr.version)


def _compare_versions(test_context, src_vr, dst_vr, run_ids_equal, compare_stages=False):
    compare_versions(to_MlflowContext(test_context), src_vr, dst_vr, 
        compare_names=False, 
        run_ids_equal=run_ids_equal, 
        compare_stages=compare_stages
    )
