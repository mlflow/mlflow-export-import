"""
Registered model utilities.
"""

import time
import mlflow
from mlflow.exceptions import RestException

from mlflow_export_import.common.iterators import SearchModelVersionsIterator
from mlflow_export_import.common.timestamp_utils import fmt_ts_millis, adjust_timestamps
from mlflow_export_import.common import utils
from mlflow_export_import.common import filesystem as _filesystem
from mlflow_export_import.common import ws_permissions_utils, uc_permissions_utils
from mlflow_export_import.client.client_utils import create_http_client, create_dbx_client

_logger = utils.getLogger(__name__)


def is_unity_catalog_model(name):
    return len(name.split(".")) == 3


def model_names_same_registry(name1, name2):
    return \
        is_unity_catalog_model(name1) and is_unity_catalog_model(name2) or \
        not is_unity_catalog_model(name1) and not is_unity_catalog_model(name2)


def model_names_same_registry_nonucsrc_uctgt(name1, name2):
    return \
        not is_unity_catalog_model(name1) and is_unity_catalog_model(name2)


def create_model(client, model_name, model_dct, import_metadata):
    """
    Creates a registered model if it does not exist, and returns the model in either case.
    """
    try:
        if import_metadata:
            tags = utils.mk_tags_dict(model_dct.get("tags"))
            client.create_registered_model(model_name, tags, model_dct.get("description"))
        else:
            client.create_registered_model(model_name)
        _logger.info(f"Created new registered model '{model_name}'")
        return True
    except Exception as e:
        _logger.info(f"except Exception trigger, error for '{model_name}': {e}")
    except RestException as e:
        if e.error_code != "RESOURCE_ALREADY_EXISTS":
            raise e
        _logger.info(f"Registered model '{model_name}' already exists")
        return False


def delete_model(client, model_name, sleep_time=5):
    """
    Delete a registered model and all its versions.
    """
    try:
        # versions = SearchModelVersionsIterator(client, filter=f"name='{model_name}'")
        versions = SearchModelVersionsIterator(client, filter=f""" name="{model_name}" """)  #birbal added
        _logger.info(f"Deleting model '{model_name}' and its versions")
        for vr in versions:
            msg = utils.get_obj_key_values(vr, [ "name", "version", "current_stage", "status", "run_id"  ])
            _logger.info(f"  Deleting model version: {msg}")
            if not is_unity_catalog_model(model_name) and vr.current_stage != "Archived":
                client.transition_model_version_stage (model_name, vr.version, "Archived")
                time.sleep(sleep_time) # Wait until stage transition takes hold
            client.delete_model_version(model_name, vr.version)
        client.delete_registered_model(model_name)
    # except RestException: #birbal commented out
    except Exception as e:
        _logger.error(f"Error deleting modfel {model_name}. Error: {e}")
        


def list_model_versions(client, model_name, get_latest_versions=False):
    """
    List 'all' or the 'latest' versions of registered model.
    """
    if is_unity_catalog_model(model_name):
        # versions = SearchModelVersionsIterator(client, filter=f"name='{model_name}'")
        versions = SearchModelVersionsIterator(client, filter=f""" name="{model_name}" """) #birbal added
        # JIRA: ES-834105 - UC-ML MLflow search_registered_models and search_model_versions do not return tags and aliases - 2023-08-21
        return [ client.get_model_version(vr.name, vr.version) for vr in versions ]
    else:
        if get_latest_versions:
            return client.get_latest_versions(model_name)
        else:
            # return list(SearchModelVersionsIterator(client, filter=f"name='{model_name}'"))
            return list(SearchModelVersionsIterator(client, filter=f""" name="{model_name}" """)) #birbal added


def search_model_versions(client, filter):
    """
    Wrapper around MlflowClient.search_model_versions to account for missing aliases and tags in returned ModelVersion.
    Makes a call to MlflowClient.get_model_version for each version. Hardly performant.
     - Missing aliases - https://github.com/mlflow/mlflow/issues/9783 - [BUG] MlflowClient.search_model_versions does not return aliases
     - Missing tags - ES-834105 - UC-ML MLflow search_registered_models and search_model_versions do not return tags and aliases
    """
    versions = client.search_model_versions(filter)
    return [ client.get_model_version(vr.name, vr.version) for vr in versions ]


def export_version_model(client, version, output_dir):
    """
    Exports the model version's "cached" MLflow model.
    :param client: MLflowClient.
    :param version: Model version.
    :param output_dir: Output directory.
    :return: Result of MlflowClient.get_model_version_download_uri().
    """
    download_uri = f"models:/{version.name}/{version.version}"
    _logger.info(f"Exporting model version 'cached model' to: '{output_dir}'")
    local_dir = mlflow.artifacts.download_artifacts(
        artifact_uri = download_uri,
        dst_path = _filesystem.mk_local_path(output_dir)
    )
    return download_uri


def show_versions(model_name, versions, msg):
    """
    Display as table registered model versions.
     """
    import pandas as pd
    from tabulate import tabulate
    versions = [ [
           int(vr.version),
           vr.current_stage,
           vr.status,
           vr.run_id,
           fmt_ts_millis(vr.creation_timestamp),
           fmt_ts_millis(vr.last_updated_timestamp),
           vr.description
       ] for vr in versions ]
    df = pd.DataFrame(versions, columns = [
        "version",
        "current_stage",
        "status",
        "run_id",
        "creation_timestamp",
        "last_updated_timestamp",
        "description"
    ])
    df.sort_values(by=["version"], ascending=False, inplace=True)
    print(f"\n'{msg}' {len(versions)} versions for model '{model_name}'")
    print(tabulate(df, headers="keys", tablefmt="psql", showindex=False))


def model_version_to_dict(version):
    """
    Convert a ModelVersion to a dictionary.
    1. Per doc, aliases are supposed to be a list of strings but are acutally a ProtoBuf and therefore
       JSON serialization fails.
       https://mlflow.org/docs/latest/python_api/mlflow.entities.html#mlflow.entities.model_registry.ModelVersion.aliases
    2. Wot! Difference between ModelVersion property 'creation_timestamp' and attribute 'creation_timestamp'
    """
    dct = {}
    for k,v in utils.strip_underscores(version).items():
        if k == "aliases": # type is google._upb._message.RepeatedScalarContainer
            dct[k] = [ str(x) for x in v ]
        else:
            if k == "creation_time":  # Wot!
                k = "creation_timestamp"
            dct[k] = v
    return dct


def dump_model_version(version, title=None):
    from mlflow_export_import.common import dump_utils
    dct = model_version_to_dict(version)
    dct = model_version_to_dict(version)
    adjust_timestamps(dct, ["creation_timestamp", "last_updated_timestamp"])
    dump_utils.dump_as_json(dct, title)


def dump_model_versions(client, model_name):
    """
    Display as table 'latest' and 'all' registered model versions.
    """
    if not is_unity_catalog_model(model_name):
        versions = client.get_latest_versions(model_name)
        show_versions(model_name, versions, "Latest")
    versions = SearchModelVersionsIterator(client, filter=f"name='{model_name}'")
    show_versions(model_name, list(versions), "All")


def get_registered_model(mlflow_client, model_name, get_permissions=False):
    """
    Get registered model and optionally its permissions.
    """
    http_client = create_http_client(mlflow_client, model_name)
    if get_permissions and utils.calling_databricks():
        if is_unity_catalog_model(model_name):
            _model = http_client.get("registered-models/get", {"name": model_name})
            model = _model["registered_model"]
            permissions = uc_permissions_utils.get_permissions(mlflow_client, model_name)
        else:
            dbx_client = create_dbx_client(mlflow_client)
            _model = http_client.get("databricks/registered-models/get", { "name": model_name })
            model = _model.pop("registered_model_databricks", None)
            permissions = ws_permissions_utils.get_model_permissions_by_id(dbx_client, model["id"])
            _model["registered_model"] = model
    else:
        _model = http_client.get("registered-models/get", {"name": model_name})
        model = _model["registered_model"]
        permissions = None
    adjust_timestamps(model, ["creation_timestamp", "last_updated_timestamp"])
    if permissions:
        model["permissions"] = permissions
    model.pop("latest_versions", None)
    return model


def update_model_permissions(mlflow_client, dbx_client, model_name, perms, nonucsrc_uctgt = False): #birbal added nonucsrc_uctgt parameter
    if perms:
        _logger.info(f"Updating permissions for registered model '{model_name}'")
        if is_unity_catalog_model(model_name) and not nonucsrc_uctgt: #birbal added
            uc_permissions_utils.update_permissions(mlflow_client, model_name, perms)
        elif is_unity_catalog_model(model_name) and nonucsrc_uctgt: #birbal added
            uc_permissions_utils.update_permissions_nonucsrc_uctgt(mlflow_client, model_name, perms)
        else:
            _model = dbx_client.get("mlflow/databricks/registered-models/get", { "name": model_name })
            _model = _model["registered_model_databricks"]
            model_id = _model["id"]
            ws_permissions_utils.update_permissions(dbx_client, perms, "registered-model", model_name, model_id)
    else:
        _logger.info(f"No permissions to update for registered model '{model_name}'")
