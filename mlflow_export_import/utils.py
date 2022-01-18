import os
import json
import time
from tabulate import tabulate
import pandas as pd
import mlflow
from . import mk_local_path

TAG_PREFIX_METADATA = "mlflow_export_import.metadata"
TAG_PREFIX_SRC_RUN = "mlflow_export_import.source_run"
TAG_PREFIX_MLFLOW = "mlflow."
TAG_PARENT_ID = "mlflow.parentRunId"

# Databricks tags that cannot be set
_databricks_skip_tags = set([
  "mlflow.user",
  "mlflow.log-model.history"
  ])

def create_mlflow_tags_for_databricks_import(tags):
    if importing_into_databricks(): 
        tags = { k:v for k,v in tags.items() if not k in _databricks_skip_tags }
    return tags

def create_tags_for_metadata(src_client, run, export_metadata_tags):
    """ Create destination tags from source run """
    tags = run.data.tags.copy()
    for k in _databricks_skip_tags:
        tags.pop(k, None)
    if export_metadata_tags:
        uri = mlflow.tracking.get_tracking_uri()
        tags[TAG_PREFIX_METADATA+".tracking_uri"] = uri
        dbx_host = os.environ.get("DATABRICKS_HOST",None)
        if dbx_host is not None:
            tags[TAG_PREFIX_METADATA+".DATABRICKS_HOST"] = dbx_host
        now = int(time.time()+.5)
        snow = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(now))
        tags[TAG_PREFIX_METADATA+".timestamp"] = str(now)
        tags[TAG_PREFIX_METADATA+".timestamp_nice"] = snow
        tags[TAG_PREFIX_METADATA+".user_id"] = run.info.user_id
        tags[TAG_PREFIX_METADATA+".run_id"] =  str(run.info.run_id)
        tags[TAG_PREFIX_METADATA+".experiment_id"] = run.info.experiment_id
        tags[TAG_PREFIX_METADATA+".artifact_uri"] = run.info.artifact_uri
        tags[TAG_PREFIX_METADATA+".status"] = run.info.status
        tags[TAG_PREFIX_METADATA+".lifecycle_stage"] = run.info.lifecycle_stage
        tags[TAG_PREFIX_METADATA+".start_time"] = run.info.start_time
        tags[TAG_PREFIX_METADATA+".end_time"] = run.info.end_time
        #tags[TAG_PREFIX_METADATA+".status"] = run.info.status
        exp = src_client.get_experiment(run.info.experiment_id)
        tags[TAG_PREFIX_METADATA+".experiment_name"] = exp.name
    tags = { k:v for k,v in sorted(tags.items()) }
    return tags

def set_dst_user_id(tags, user_id, use_src_user_id):
    if importing_into_databricks():
        return
    from mlflow.entities import RunTag
    from mlflow.utils.mlflow_tags import MLFLOW_USER
    user_id = user_id if use_src_user_id else get_user_id()
    tags.append(RunTag(MLFLOW_USER,user_id ))

def get_now_nice():
    now = int(time.time()+.5)
    return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(now))

def strip_underscores(obj):
    return { k[1:]:v for (k,v) in obj.__dict__.items() }

def write_json_file(fs, path, dct):
    fs.write(path, json.dumps(dct,indent=2)+"\n")

def write_file(path, content):
    with open(mk_local_path(path), 'wb') as f:
        f.write(content)

def read_json_file(path):
    with open(mk_local_path(path), "r") as f:
        return json.loads(f.read())

def string_to_list(list_as_string):
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

client = mlflow.tracking.MlflowClient()

def get_experiments(experiments):
    if isinstance(experiments,str):
        if experiments == "all":
            experiments = [ exp.experiment_id for exp in client.list_experiments() ]
        elif experiments.endswith("*"):
            exp_prefix = experiments[:-1]
            experiments = [ exp.experiment_id for exp in client.list_experiments() if exp.name.startswith(exp_prefix) ] # Wish there was an experiment search method for efficiency
        else:
            experiments = experiments.split(",")
    return experiments

def show_table(title, lst, columns):
    print(title)
    df = pd.DataFrame(lst, columns = columns)
    print(tabulate(df, headers="keys", tablefmt="psql", showindex=False))
