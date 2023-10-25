from mlflow_export_import.model.export_model import export_model
from mlflow_export_import.model.import_model import import_model
from mlflow_export_import.common import dump_utils
from mlflow_export_import.common import model_utils

from tests.core import to_MlflowContext
from tests.compare_utils import compare_models_with_versions
from tests.databricks.init_tests import workspace_src, workspace_dst
from tests.databricks.init_tests import test_context
from tests.databricks import local_utils

num_versions = 3

def _init(test_context, is_uc):
    src_model_name = local_utils.mk_model_name(workspace_src, is_uc)

    src_vrs = [ local_utils.create_version(test_context.mlflow_client_src, src_model_name) for _ in range(num_versions) ]
    src_model = src_vrs[0][1]
    src_vrs = [ vr[0] for vr in src_vrs ]
    for vr in src_vrs:
        dump_utils.dump_obj(vr, f"SRC Version {vr.version}")

    export_model(
        mlflow_client = test_context.mlflow_client_src,
        model_name = src_model.name,
        output_dir = test_context.output_dir
    )
    dst_model_name = local_utils.mk_model_name(workspace_dst, is_uc)
    import_model(
        mlflow_client = test_context.mlflow_client_dst,
        model_name = dst_model_name,
        experiment_name = local_utils.mk_experiment_name(workspace=workspace_dst),
        input_dir = test_context.output_dir
    )
    dst_model = test_context.mlflow_client_dst.get_registered_model(dst_model_name)
    dst_vrs = model_utils.list_model_versions(test_context.mlflow_client_dst, dst_model.name)
    assert len(dst_vrs) == num_versions
    for vr in dst_vrs:
        dump_utils.dump_obj(vr, f"DST Version {vr.version}")

    return src_model, dst_model


def test_registered_model(test_context, is_uc):
    src_model, dst_model = _init(test_context, is_uc)
    compare_models_with_versions(to_MlflowContext(test_context), src_model, dst_model, compare_names=False)
