from mlflow_export_import.common.source_tags import ExportTags
from . import compare_utils


def compare_model_versions(src_vr, dst_vr, add_copy_system_tags=False):
    assert src_vr.description == dst_vr.description
    assert src_vr.aliases == dst_vr.aliases
    if add_copy_system_tags:
        src_tags = { k:v for k,v in src_vr.tags.items() if not k.startswith(ExportTags.PREFIX_ROOT) }
        dst_tags = { k:v for k,v in dst_vr.tags.items() if not k.startswith(ExportTags.PREFIX_ROOT) }
        assert src_tags == dst_tags
    else:
        assert src_vr.tags == dst_vr.tags


def compare_runs(mlflow_context, src_vr, dst_vr):
    src_run = mlflow_context.client_src.get_run(src_vr.run_id)
    dst_run = mlflow_context.client_dst.get_run(dst_vr.run_id)
    compare_utils.compare_runs(mlflow_context, src_run, dst_run)
