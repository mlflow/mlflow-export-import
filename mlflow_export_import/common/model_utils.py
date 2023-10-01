import time
import mlflow
from mlflow.exceptions import RestException
from mlflow.entities.model_registry.model_version_status import ModelVersionStatus

from mlflow_export_import.common.iterators import SearchModelVersionsIterator
from mlflow_export_import.common.timestamp_utils import fmt_ts_millis
from mlflow_export_import.common import utils
from mlflow_export_import.common import filesystem as _filesystem

_logger = utils.getLogger(__name__)


def is_unity_catalog_model(name):
    return len(name.split(".")) == 3


def create_model(client, model_name, tags=None, description=None):
    """ 
    Creates a registered model if it does not exist, and returns the model in either case.
    """
    client = client or mlflow.MlflowClient()
    try:
        model = client.create_registered_model(model_name, tags, description)
        _logger.info(f"Created new registered model '{model_name}'")
        return model
    except RestException as e:
        if e.error_code != "RESOURCE_ALREADY_EXISTS":
            raise e
        _logger.info(f"Registered model '{model_name}' already exists")
        return client.get_registered_model(model_name)


def delete_model(client, model_name, sleep_time=5):
    """ 
    Delete a registered model and all its versions.
    """
    try:
        versions = SearchModelVersionsIterator(client, filter=f"name='{model_name}'")
        _logger.info(f"Deleting model '{model_name}' and its versions")
        for vr in versions:
            msg = utils.get_obj_key_values(vr, [ "name", "version", "current_stage", "status", "run_id"  ])
            _logger.info(f"  Deleting model version: {msg}")
            if not is_unity_catalog_model(model_name) and vr.current_stage != "Archived":
                client.transition_model_version_stage (model_name, vr.version, "Archived")
                time.sleep(sleep_time) # Wait until stage transition takes hold
            client.delete_model_version(model_name, vr.version)
        client.delete_registered_model(model_name)
    except RestException:
        pass


def list_model_versions(client, model_name, get_latest_versions=False):
    """
    List 'all' or the 'latest' versions of registered model.
    """
    if is_unity_catalog_model(model_name):
        versions = SearchModelVersionsIterator(client, filter=f"name='{model_name}'")
        # JIRA: ES-834105 - UC-ML MLflow search_registered_models and search_model_versions do not return tags and aliases - 2023-08-21
        return [ client.get_model_version(vr.name, vr.version) for vr in versions ]
    else:
        if get_latest_versions:
            return client.get_latest_versions(model_name)
        else:
            return list(SearchModelVersionsIterator(client, filter=f"name='{model_name}'"))


def wait_until_version_is_ready(client, model_name, model_version, sleep_time=1, iterations=100):
    """ 
    Due to blob eventual consistency, wait until a newly created version is in READY state.
    """
    start = time.time()
    for _ in range(iterations):
        vr = client.get_model_version(model_name, model_version.version)
        status = ModelVersionStatus.from_string(vr.status)
        msg = utils.get_obj_key_values(vr, [ "name", "version", "current_stage", "status" ])
        _logger.info(f"Model version transition: {msg}")
        if status == ModelVersionStatus.READY:
            break
        time.sleep(sleep_time)
    end = time.time()
    _logger.info(f"Waited {round(end-start,2)} seconds")


def export_version_model(client, version, output_dir):
    """
    Exports the model version's "cached" MLflow model.
    :param client: MLflowClient.
    :param version: Model version.
    :param output_dir: Output directory.
    :return: Result of MlflowClient.get_model_version_download_uri().
    """
    download_uri = client.get_model_version_download_uri(version.name, version.version)
    _logger.info(f"Exporting model version 'cached model' to: '{output_dir}'")
    mlflow.artifacts.download_artifacts(
        artifact_uri = download_uri,
        dst_path = _filesystem.mk_local_path(output_dir),
        tracking_uri = client._tracking_client.tracking_uri
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


def dump_model_versions(client, model_name):
    """ 
    Display as table 'latest' and 'all' registered model versions.
    """
    if not is_unity_catalog_model(model_name):
        versions = client.get_latest_versions(model_name)
        show_versions(model_name, versions, "Latest")
    versions = SearchModelVersionsIterator(client, filter=f"name='{model_name}'")
    show_versions(model_name, list(versions), "All")
