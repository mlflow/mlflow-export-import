from mlflow_export_import.model_version.export_model_version import export_model_version
from mlflow_export_import.model_version.import_model_version import import_model_version
from mlflow_export_import.common.mlflow_utils import get_experiment_description, set_experiment_description

from tests.core import to_MlflowContext
from tests.compare_utils import compare_versions
from tests.databricks.init_tests import workspace_src, workspace_dst
from tests.databricks import local_utils
from tests.databricks.init_tests import test_context

def test_import_metadata_false(test_context, is_uc):
    src_model, dst_model, src_exp, dst_exp = run_test(test_context, import_metadata=False, is_uc=is_uc)
    assert src_model.description != dst_model.description
    assert src_model.tags != dst_model.tags
    assert get_experiment_description(src_exp) != get_experiment_description(dst_exp)
    assert src_exp.tags != dst_exp.tags

def test_import_metadata_true(test_context, is_uc):
    src_model, dst_model, src_exp, dst_exp = run_test(test_context, import_metadata=True, is_uc=is_uc)
    assert src_model.description == dst_model.description
    assert src_model.tags == dst_model.tags
    assert get_experiment_description(src_exp) == get_experiment_description(dst_exp)

    _remove_system_tags(src_exp)
    _remove_system_tags(dst_exp)
    assert src_exp.tags == dst_exp.tags


def run_test(test_context, import_metadata, is_uc):
    src_client = test_context.mlflow_client_src
    dst_client = test_context.mlflow_client_dst

    src_model_name = local_utils.mk_model_name(workspace_src, is_uc)
    src_vr, _ = local_utils.create_version(src_client, src_model_name)

    src_run = src_client.get_run(src_vr.run_id)
    set_experiment_description(src_client, src_run.info.experiment_id, "Hello sunrise")
    src_exp = src_client.get_experiment(src_run.info.experiment_id)

    export_model_version(
        model_name = src_vr.name,
        version = src_vr.version,
        output_dir = test_context.output_dir,
        export_version_model = False,
        mlflow_client = src_client
    )

    dst_model_name = local_utils.mk_model_name(workspace_dst, is_uc)
    dst_exp_name = local_utils.mk_experiment_name(workspace=workspace_dst)
    dst_vr = import_model_version(
        model_name = dst_model_name,
        experiment_name = dst_exp_name,
        input_dir = test_context.output_dir,
        create_model = True,
        import_source_tags = False,
        import_metadata = import_metadata,
        mlflow_client = dst_client
    )
    compare_versions(to_MlflowContext(test_context), src_vr, dst_vr, False, False, compare_stages=False)

    src_model = src_client.get_registered_model(src_vr.name)
    dst_model = dst_client.get_registered_model(dst_vr.name)

    dst_run = dst_client.get_run(dst_vr.run_id)
    dst_exp = dst_client.get_experiment(dst_run.info.experiment_id)

    return src_model, dst_model, src_exp, dst_exp


# NOTE: should be in  mlflow.utils.mlflow_tags
MLFLOW_EXPERIMENT_SOURCE_NAME = "mlflow.experiment.sourceName"
MLFLOW_OWNER_ID = "mlflow.ownerId"

def _remove_system_tags(exp):
    exp.tags.pop(MLFLOW_EXPERIMENT_SOURCE_NAME, None)
    exp.tags.pop(MLFLOW_OWNER_ID, None)
