import os

from mlflow_export_import.common.dump_utils import dump_mlflow_client
from mlflow_export_import.copy import copy_model_version

from tests.core import MlflowContext
from tests.compare_utils import compare_versions

from . init_tests import mlflow_context
from . oss_utils_test import mk_test_object_name_default
from . oss_utils_test import create_experiment
from . test_model_version import create_model_version


def test_with_experiment(mlflow_context):
    dump_mlflow_client(mlflow_context.client_src,"SRC Client")
    dump_mlflow_client(mlflow_context.client_dst,"DST Client")
    dst_exp = create_experiment(mlflow_context.client_src)
    vr, _ = create_model_version(mlflow_context)
    dst_model_name = mk_test_object_name_default()

    src_vr, dst_vr = copy_model_version.copy(
        src_model_name = vr.name,
        src_model_version = vr.version,
        dst_model_name = dst_model_name,
        dst_experiment_name = dst_exp.name,
        src_tracking_uri = mlflow_context.client_src.tracking_uri,
        dst_tracking_uri = mlflow_context.client_dst.tracking_uri,
        verbose = False
    )
    assert vr == src_vr
    compare_versions(mlflow_context, src_vr, dst_vr, False, False)

    assert src_vr.run_id != dst_vr.run_id
    assert dst_vr == mlflow_context.client_dst.get_model_version(dst_vr.name, dst_vr.version)


def test_without_experiment(mlflow_context):
    vr, _ = create_model_version(mlflow_context)
    dst_model_name = mk_test_object_name_default()
    src_vr, dst_vr = copy_model_version.copy(
        src_model_name = vr.name,
        src_model_version = vr.version,
        dst_model_name = dst_model_name,
        dst_experiment_name = None,
        src_tracking_uri = mlflow_context.client_src.tracking_uri,
        dst_tracking_uri = mlflow_context.client_src.tracking_uri,
        verbose = False
    )
    assert vr == src_vr
    mlflow_context = _mk_one_tracking_server_context(mlflow_context)
    compare_versions(mlflow_context, src_vr, dst_vr, False, True)
    assert src_vr.run_id == dst_vr.run_id
    assert dst_vr == mlflow_context.client_src.get_model_version(dst_vr.name, dst_vr.version)


def test_without_dst_tracking_uri(mlflow_context):
    dst_exp = create_experiment(mlflow_context.client_src)
    vr, _ = create_model_version(mlflow_context)
    dst_model_name = mk_test_object_name_default()

    src_vr, dst_vr = copy_model_version.copy(
        src_model_name = vr.name,
        src_model_version = vr.version,
        dst_model_name = dst_model_name,
        dst_experiment_name = dst_exp.name,
        #src_tracking_uri = mlflow_context.client_src.tracking_uri,
        #dst_tracking_uri = mlflow_context.client_dst.tracking_uri,
        verbose = False
    )
    mlflow_context = MlflowContext(
        mlflow_context.client_src,
        mlflow_context.client_src,
        mlflow_context.output_dir,
        os.path.join(mlflow_context.output_dir,"run")
    )
    assert vr == src_vr
    compare_versions(mlflow_context, src_vr, dst_vr, False, False)
    assert src_vr.run_id != dst_vr.run_id
    assert dst_vr == mlflow_context.client_dst.get_model_version(dst_vr.name, dst_vr.version)


def test_with_experiment_and_copy_tags(mlflow_context):
    dump_mlflow_client(mlflow_context.client_src, "SRC Client")
    dump_mlflow_client(mlflow_context.client_dst, "DST Client")
    dst_exp = create_experiment(mlflow_context.client_src)
    vr, _ = create_model_version(mlflow_context)
    dst_model_name = mk_test_object_name_default()

    src_vr, dst_vr = copy_model_version.copy(
        src_model_name = vr.name,
        src_model_version = vr.version,
        dst_model_name = dst_model_name,
        dst_experiment_name = dst_exp.name,
        src_tracking_uri = mlflow_context.client_src.tracking_uri,
        dst_tracking_uri = mlflow_context.client_dst.tracking_uri,
        copy_lineage_tags = True,
        verbose = False
    )
    compare_versions(mlflow_context, src_vr, dst_vr, False, False)
    assert src_vr.run_id != dst_vr.run_id
    assert dst_vr == mlflow_context.client_dst.get_model_version(dst_vr.name, dst_vr.version)


def _mk_one_tracking_server_context(mlflow_context):
    return MlflowContext(
        mlflow_context.client_src,
        mlflow_context.client_src,
        mlflow_context.output_dir,
        os.path.join(mlflow_context.output_dir, "run")
    )
