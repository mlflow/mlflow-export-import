import os
import json
import pandas as pd
from tabulate import tabulate

import mlflow
from . import mk_local_path


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


def set_dst_user_id(tags, user_id, use_src_user_id):
    if importing_into_databricks():
        return
    from mlflow.entities import RunTag
    from mlflow.utils.mlflow_tags import MLFLOW_USER
    user_id = user_id if use_src_user_id else get_user_id()
    tags.append(RunTag(MLFLOW_USER,user_id ))


# Miscellaneous 

def _read_manifest_json_file(input_dir, filename):
    """ Handle depcrecated "manifest.json" instead of current MLflow object file name such as "experiments.json". Former file name will be eventually removed. """
    path = os.path.join(input_dir, filename)
    if not os.path.exists(path):
        path = os.path.join(input_dir, "manifest.json") # NOTE: old deprecated, will be eventually removed
    return path


def strip_underscores(obj):
    return { k[1:]:v for (k,v) in obj.__dict__.items() }


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


def show_table(title, lst, columns):
    print(title)
    df = pd.DataFrame(lst, columns = columns)
    print(tabulate(df, headers="keys", tablefmt="psql", showindex=False))
