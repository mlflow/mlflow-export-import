import os
import json
import time
from tabulate import tabulate
import pandas as pd

import mlflow
from . import mk_local_path
from mlflow_export_import.source_tags import ExportTags, MlflowTags


# Databricks tags that cannot be set
_DATABRICKS_SKIP_TAGS = set([
  "mlflow.user",
  "mlflow.log-model.history",
  "mlflow.rootRunId"
  ])


def create_mlflow_tags_for_databricks_import(tags):
    if importing_into_databricks(): 
        tags = { k:v for k,v in tags.items() if not k in _DATABRICKS_SKIP_TAGS }
    return tags


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
        for k,v in strip_underscores(run.info).items():
            tags[f"{ExportTags.TAG_PREFIX_RUN_INFO}.{k}"] = str(v) # NOTE: tag values must be strings
        for k,v in mlflow_system_tags.items():
            tags[k.replace(MlflowTags.TAG_PREFIX,ExportTags.TAG_PREFIX_MLFLOW+".")] = v
    tags = { k:v for k,v in sorted(tags.items()) }
    return tags


def set_dst_user_id(tags, user_id, use_src_user_id):
    if importing_into_databricks():
        return
    from mlflow.entities import RunTag
    from mlflow.utils.mlflow_tags import MLFLOW_USER
    user_id = user_id if use_src_user_id else get_user_id()
    tags.append(RunTag(MLFLOW_USER,user_id ))


# Timestamp format methods

TS_FORMAT = "%Y-%m-%d %H:%M:%S"
ts_now_seconds = round(time.time())
ts_now_fmt_utc = time.strftime(TS_FORMAT, time.gmtime(ts_now_seconds))
ts_now_fmt_local = time.strftime(TS_FORMAT, time.localtime(ts_now_seconds))

def get_now_nice(as_utc=False):
    return fmt_ts_seconds(round(time.time()), as_utc)

def fmt_ts_millis(millis, as_utc=False):
    return fmt_ts_seconds(round(millis/1000), as_utc)

def fmt_ts_seconds(seconds, as_utc=False):
    ts_format = "%Y-%m-%d %H:%M:%S"
    if as_utc:
        ts = time.gmtime(seconds)
    else:
        ts = time.localtime(seconds)
    return time.strftime(ts_format, ts)


def create_export_times():
    return {
        "seconds": ts_now_seconds,
        "local_time": ts_now_fmt_local,
        "utc_time": ts_now_fmt_local
    }

def create_export_info():
    return {
        "mlflow_version": mlflow.__version__,
        "mlflow_tracking_uri": mlflow.get_tracking_uri(),
        ExportTags.TAG_EXPORT_TIME: {
            "seconds": ts_now_seconds,
            "local_time": ts_now_fmt_local,
            "utc_time": ts_now_fmt_utc
        }
    }


# Miscellaneous 

def strip_underscores(obj):
    return { k[1:]:v for (k,v) in obj.__dict__.items() }


def write_json_file(fs, path, dct):
    fs.write(path, json.dumps(dct,indent=2)+"\n")


def write_file(path, content):
    with open(mk_local_path(path), "wb" ) as f:
        f.write(content)


def read_json_file(path):
    with open(mk_local_path(path), "r", encoding="utf-8") as f:
        return json.loads(f.read())


def string_to_list(list_as_string):
    if list_as_string == None:
        return []
    lst = list_as_string.split(",")
    if "" in lst: lst.remove("")
    return lst


def get_user_id():
    from mlflow.tracking.context.default_context import _get_user
    return _get_user()


def nested_tags(dst_client, run_ids_mapping):
    """
    Set the new parentRunId for new imported child runs.
    """
    for _,v in run_ids_mapping.items():
        src_parent_run_id = v.get("src_parent_run_id",None)
        if src_parent_run_id:
            dst_run_id = v["dst_run_id"]
            dst_parent_run_id = run_ids_mapping[src_parent_run_id]["dst_run_id"]
            dst_client.set_tag(dst_run_id, "mlflow.parentRunId", dst_parent_run_id)


def importing_into_databricks():
    return mlflow.tracking.get_tracking_uri().startswith("databricks")


def create_common_manifest(duration):
    return {
        "info": {
            "mlflow_version": mlflow.__version__,
            "mlflow_tracking_uri": mlflow.get_tracking_uri(),
            "export_time": get_now_nice(),
            "duration": duration
        }
    }


def show_table(title, lst, columns):
    print(title)
    df = pd.DataFrame(lst, columns = columns)
    print(tabulate(df, headers="keys", tablefmt="psql", showindex=False))
