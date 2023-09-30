from mlflow_export_import.model.export_model import export_model
from mlflow_export_import.model.import_model import import_model
from mlflow_export_import.common import dump_utils
from mlflow_export_import.common import model_utils

from tests.core import to_MlflowContext
from tests.compare_utils import compare_models
from tests.compare_copy_model_version_utils import compare_model_versions, compare_runs
from tests.databricks.init_tests import workspace_src, workspace_dst
from tests.databricks.init_tests import test_context
from tests.databricks import local_utils


def _init(test_context):
    src_model_name = local_utils.mk_uc_model_name(workspace_src)
    src_vr, src_model = local_utils.create_version(test_context.mlflow_client_src, src_model_name)
    dump_utils.dump_obj(src_vr, "SRC Version")

    export_model(
        mlflow_client = test_context.mlflow_client_src,
        model_name = src_model.name,
        output_dir = test_context.output_dir
    )
    dst_model_name = local_utils.mk_uc_model_name(workspace_dst)
    import_model(
        mlflow_client = test_context.mlflow_client_dst,
        model_name = dst_model_name,
        experiment_name = local_utils.mk_experiment_name(workspace=workspace_dst),
        input_dir = test_context.output_dir
    )
    dst_model = test_context.mlflow_client_dst.get_registered_model(dst_model_name)
    dst_vrs = model_utils.list_model_versions(test_context.mlflow_client_dst, dst_model.name)
    assert len(dst_vrs) == 1
    dst_vr = dst_vrs[0]
    dump_utils.dump_obj(dst_vr, "DST Version")

    return src_model, src_vr, dst_model, dst_vr


def test_registered_model(test_context):
    src_model, src_vr, dst_model, dst_vr  = _init(test_context)
    compare_models(src_model, dst_model, compare_name=False)
    compare_model_versions(src_vr, dst_vr)
    compare_runs(to_MlflowContext(test_context), src_vr, dst_vr)

