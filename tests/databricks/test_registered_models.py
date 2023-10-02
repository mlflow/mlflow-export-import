from mlflow_export_import.model.export_model import export_model
from mlflow_export_import.model.import_model import import_model

from tests.core import to_MlflowContext
from tests.compare_utils import compare_models_with_versions
from . init_tests import workspace_dst
from . init_tests import test_context
from . import local_utils

def _init(test_context):
    src_model_name = local_utils.mk_test_object_name_default()
    _, src_model = local_utils.create_version(test_context.mlflow_client_src, src_model_name, "Production")
    export_model(
        mlflow_client = test_context.mlflow_client_src,
        model_name = src_model.name,
        output_dir = test_context.output_dir
    )
    dst_model_name = src_model.name
    import_model(
        mlflow_client = test_context.mlflow_client_dst,
        model_name = dst_model_name,
        experiment_name = local_utils.mk_experiment_name(workspace=workspace_dst),
        input_dir = test_context.output_dir
    )
    dst_model = test_context.mlflow_client_dst.get_registered_model(dst_model_name)
    return src_model, dst_model


def test_registered_model(test_context):
    src_model, dst_model = _init(test_context)
    compare_models_with_versions(to_MlflowContext(test_context), src_model, dst_model)
