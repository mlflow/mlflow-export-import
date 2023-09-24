from mlflow_export_import.model.export_model import export_model
from mlflow_export_import.model.import_model import import_model

from tests.compare_utils import compare_models_with_versions
from . init_tests import workspace_dst
from . init_tests import test_context
from . import local_utils
from . local_utils import to_MlflowContext

def _init(test_context):
    model_name_src = local_utils.mk_test_object_name_default()
    _, model_src = local_utils.create_version(test_context.mlflow_client_src, model_name_src, "Production")
    export_model(
        mlflow_client = test_context.mlflow_client_src,
        model_name = model_src.name,
        output_dir = test_context.output_dir
    )
    model_name_dst = model_src.name
    import_model(
        mlflow_client = test_context.mlflow_client_dst,
        model_name = model_name_dst,
        experiment_name = local_utils.mk_experiment_name(workspace=workspace_dst),
        input_dir = test_context.output_dir
    )
    model_dst = test_context.mlflow_client_dst.get_registered_model(model_name_dst)
    return model_src, model_dst


def test_registered_model(test_context):
    model_src, model_dst = _init(test_context)
    compare_models_with_versions(to_MlflowContext(test_context), model_src, model_dst)
