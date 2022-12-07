
import os
import mlflow
from mlflow_export_import.common import utils
from mlflow_export_import.common.timestamp_utils import ts_now_seconds, ts_now_fmt_local, ts_now_fmt_utc
from mlflow_export_import.common.source_tags import ExportTags, MlflowTags


def _create_source_tags(src_client, tags, run):
    tags[f"{ExportTags.TAG_PREFIX_METADATA}.mlflow_version"] = mlflow.__version__
    uri = mlflow.tracking.get_tracking_uri()
    tags[f"{ExportTags.TAG_PREFIX_METADATA}.tracking_uri"] = uri
    dbx_host = os.environ.get("DATABRICKS_HOST",None)
    if dbx_host is not None:
        tags[f"{ExportTags.TAG_PREFIX_METADATA}.DATABRICKS_HOST"] = dbx_host
    tags[f"{ExportTags.TAG_PREFIX_METADATA}.timestamp"] = str(ts_now_seconds)
    tags[f"{ExportTags.TAG_PREFIX_METADATA}.timestamp_nice_local"] = ts_now_fmt_local
    tags[f"{ExportTags.TAG_PREFIX_METADATA}.timestamp_nice_utc"] = ts_now_fmt_utc
    exp = src_client.get_experiment(run.info.experiment_id)
    tags[f"{ExportTags.TAG_PREFIX_METADATA}.experiment_name"] = exp.name


def create_source_tags(src_client, run, export_source_tags):
    """ Create destination tags from source run """
    mlflow_system_tags = { k:v for k,v in run.data.tags.items() if k.startswith(MlflowTags.TAG_PREFIX) }
    tags = run.data.tags.copy()
    if export_source_tags:
        _create_source_tags(src_client, tags, run)
        for k,v in utils.strip_underscores(run.info).items():
            tags[f"{ExportTags.TAG_PREFIX_RUN_INFO}.{k}"] = str(v) # NOTE: tag values must be strings
        for k,v in mlflow_system_tags.items():
            tags[k.replace(MlflowTags.TAG_PREFIX,ExportTags.TAG_PREFIX_MLFLOW+".")] = v
    tags = { k:v for k,v in sorted(tags.items()) }
    return tags
