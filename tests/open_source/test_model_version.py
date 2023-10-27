from mlflow_export_import.common.mlflow_utils import get_experiment_description
from mlflow_export_import.model_version.export_model_version import export_model_version
from mlflow_export_import.model_version.import_model_version import import_model_version

from tests.compare_utils import compare_versions
from . init_tests import mlflow_context
from . oss_utils_test import mk_test_object_name_default
from . oss_utils_test import create_version


from dataclasses import dataclass
from typing import Any

@dataclass()
class Result:
    src_model: Any
    dst_model: Any
    src_vr: Any
    dst_vr: Any
    src_exp: Any
    dst_exp: Any


def test_import_metadata_false(mlflow_context):
    r = run_test(mlflow_context, import_metadata=False)
    assert r.src_model.description != r.dst_model.description
    assert r.src_model.tags != r.dst_model.tags
    assert get_experiment_description(r.src_exp) != get_experiment_description(r.dst_exp)
    assert r.src_exp.tags != r.dst_exp.tags

def test_import_metadata_true(mlflow_context):
    r = run_test(mlflow_context, import_metadata=True)
    assert r.src_model.description == r.dst_model.description
    assert r.src_model.tags == r.dst_model.tags
    assert get_experiment_description(r.src_exp) == get_experiment_description(r.dst_exp)
    assert r.src_exp.tags == r.dst_exp.tags

def test_not_import_stages_and_aliases(mlflow_context):
    r = run_test(mlflow_context, import_metadata=True, import_stages_and_aliases=False)
    assert r.src_model.description == r.dst_model.description
    assert r.src_model.tags == r.dst_model.tags
    assert get_experiment_description(r.src_exp) == get_experiment_description(r.dst_exp)
    assert r.src_exp.tags == r.dst_exp.tags

    assert r.src_vr.current_stage != r.dst_vr.current_stage
    assert r.src_vr.aliases != r.dst_vr.aliases


def run_test(mlflow_context, import_metadata, import_stages_and_aliases=True):
    dst_exp_name = mk_test_object_name_default()
    src_vr, src_run = create_model_version(mlflow_context)
    dst_model_name = mk_test_object_name_default()

    export_model_version(
        model_name = src_vr.name,
        version = src_vr.version,
        output_dir = mlflow_context.output_dir,
        export_version_model = False,
        mlflow_client = mlflow_context.client_src
    )

    dst_vr = import_model_version(
        model_name = dst_model_name,
        experiment_name = dst_exp_name,
        input_dir = mlflow_context.output_dir,
        create_model = True,
        import_source_tags = False,
        import_stages_and_aliases = import_stages_and_aliases,
        import_metadata = import_metadata,
        mlflow_client = mlflow_context.client_dst
    )
    compare_versions(mlflow_context, src_vr, dst_vr, False, False, compare_stages=import_stages_and_aliases)

    src_model = mlflow_context.client_src.get_registered_model(src_vr.name)
    dst_model = mlflow_context.client_dst.get_registered_model(dst_vr.name)
    src_exp = mlflow_context.client_src.get_experiment(src_run.info.experiment_id)
    dst_exp = mlflow_context.client_dst.get_experiment_by_name(dst_exp_name)

    return Result(src_model, dst_model, src_vr, dst_vr, src_exp, dst_exp)

def create_model_version(mlflow_context):
    model_name_src = mk_test_object_name_default()
    desc = "Hello decription"
    tags = { "city": "franconia" }
    mlflow_context.client_src.create_registered_model(model_name_src, tags, desc)
    return create_version(mlflow_context.client_src, model_name_src, "Production")
