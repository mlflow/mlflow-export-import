from mlflow_export_import.copy import copy_run
from . init_tests import test_context
from . import local_utils
from . import compare_utils
from . init_tests import workspace_src, workspace_dst


def _init_run_test(test_context, workspace_src, workspace_dst):
    exp_src = local_utils.create_experiment(test_context.mlflow_client_src)
    src_run = local_utils.create_run(test_context.mlflow_client_src, exp_src.experiment_id)
    dst_exp_name = local_utils.mk_experiment_name(workspace_dst)
    dst_run = copy_run.copy(
        src_run.info.run_id,
        dst_exp_name,
        workspace_src.cfg.profile,
        workspace_dst.cfg.profile
    )
    return src_run, dst_run


def test_run_same_workspace(test_context):
    src_run, dst_run = _init_run_test(test_context, workspace_src, workspace_src)
    compare_utils.compare_runs(src_run, dst_run)

def test_run_different__workspace(test_context):
    src_run, dst_run = _init_run_test(test_context, workspace_src, workspace_dst)
    compare_utils.compare_runs(src_run, dst_run)
