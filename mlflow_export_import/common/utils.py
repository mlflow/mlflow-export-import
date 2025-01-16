import os
import pandas as pd
import mlflow
from tabulate import tabulate
from enum import Enum, auto

class MLFlowImplementation(Enum):
    DATABRICKS = auto()
    AZURE_ML = auto()
    OSS = auto()

def getLogger(name):
    from mlflow_export_import.common import logging_utils
    return logging_utils.get_logger(name)

_logger = getLogger(__name__)


_calling_databricks = None

def calling_databricks(dbx_client=None):
    """
    Are we importing into Databricks?
    Check by making call to Databricks-specific API endpoint and check for 400 status code.
    """
    from mlflow_export_import.client.http_client import DatabricksHttpClient
    from mlflow_export_import.common import MlflowExportImportException

    global _calling_databricks
    if _calling_databricks is None:
        dbx_client = dbx_client or DatabricksHttpClient()
        try:
            dbx_client.get("clusters/list-node-types")
            _calling_databricks =  True
        except MlflowExportImportException:
            _calling_databricks =  False
        _logger.info(f"Calling Databricks: {_calling_databricks}")
    return _calling_databricks


# Databricks tags that cannot or should not be set
_DATABRICKS_SKIP_TAGS = {
    "mlflow.user",
    "mlflow.log-model.history",
    "mlflow.rootRunId",
    "mlflow.experiment.sourceType",
    "mlflow.experiment.sourceId"
}

_AZURE_ML_SKIP_TAGS = set([
  "mlflow.user",
  "mlflow.source.git.commit"
  ])

def create_mlflow_tags_for_databricks_import(tags):
    environment = get_import_target_implementation()
    if environment == MLFlowImplementation.DATABRICKS:
        return { k:v for k,v in tags.items() if not k in _DATABRICKS_SKIP_TAGS }
    if environment == MLFlowImplementation.AZURE_ML:
        return { k:v for k,v in tags.items() if not k in _AZURE_ML_SKIP_TAGS }
    if environment == MLFlowImplementation.OSS:
        return tags
    raise Exception("Unsupported environment")


def set_dst_user_id(tags, user_id, use_src_user_id):
    if get_import_target_implementation() in (MLFlowImplementation.DATABRICKS, 
                                              MLFlowImplementation.AZURE_ML):
        return
    from mlflow.entities import RunTag
    from mlflow.utils.mlflow_tags import MLFLOW_USER
    user_id = user_id if use_src_user_id else get_user_id()
    tags.append(RunTag(MLFLOW_USER,user_id ))

def get_import_target_implementation() -> MLFlowImplementation:
    if mlflow.tracking.get_tracking_uri().startswith("databricks"):
        return MLFlowImplementation.DATABRICKS
    if mlflow.tracking.get_tracking_uri().startswith("azureml"):
        return MLFlowImplementation.AZURE_ML
    return MLFlowImplementation.OSS

# Tags

def mk_tags_dict(tags_array):
    """
    Transform a list of key/value items to a dict.
    """
    return mk_key_value_array_dict(tags_array, "key", "value")

def mk_key_value_array_dict(kv_array, key_name, value_name):
    """
    Transforms a list of 2 item dicts to a dict.
    Example:  [{'key': 'k1', 'value': 'v1'}, {'key': 'k2', 'value': 'v2'}] ==> {'k1': 'v1', 'k2': 'v2' }
    """
    if kv_array is None:
        return {}
    return { x[key_name]:x[value_name] for x in kv_array }

# Miscellaneous


def strip_underscores(obj):
    return { k[1:]:v for (k,v) in obj.__dict__.items() }


def get_obj_key_values(obj, keys):
    return { k:v for k,v in strip_underscores(obj).items() if k in keys }


def string_to_list(list_as_string):
    if list_as_string is None:
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


def show_table(title, lst, columns):
    print(title)
    df = pd.DataFrame(lst, columns = columns)
    print(tabulate(df, headers="keys", tablefmt="psql", showindex=False))


def get_user():
    import getpass
    return getpass.getuser()


def get_threads(use_threads=False):
    return os.cpu_count() or 4 if use_threads else 1
