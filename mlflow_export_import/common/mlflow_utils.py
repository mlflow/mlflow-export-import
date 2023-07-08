import os
import mlflow
from mlflow.exceptions import RestException
from mlflow_export_import.common import MlflowExportImportException
from mlflow_export_import.common.iterators import SearchModelVersionsIterator
from mlflow_export_import.common import utils

_logger = utils.getLogger(__name__)


def get_experiment(mlflow_client, exp_id_or_name):
    """ Gets an experiment either by ID or name.  """
    exp = mlflow_client.get_experiment_by_name(exp_id_or_name)
    if exp is None:
        try:
            exp = mlflow_client.get_experiment(exp_id_or_name)
        except Exception as ex:
            raise MlflowExportImportException(ex, f"Cannot find experiment ID or name '{exp_id_or_name}'. Client: {mlflow_client}'")
    return exp


def set_experiment(mlflow_client, dbx_client, exp_name, tags=None):
    """
    Set experiment name. 
    For Databricks, create the workspace directory if it doesn't exist.
    :return: Experiment
    """
    if utils.is_importing_into_databricks():
        create_workspace_dir(dbx_client, os.path.dirname(exp_name))
    try:
        if not tags: tags = {}
        tags = utils.create_mlflow_tags_for_databricks_import(tags)
        exp_id = mlflow_client.create_experiment(exp_name, tags=tags)
        exp = mlflow_client.get_experiment(exp_id)
        _logger.info(f"Created experiment '{exp.name}' with location '{exp.artifact_location}'")
    except RestException as ex:
        if ex.error_code != "RESOURCE_ALREADY_EXISTS":
            raise MlflowExportImportException(ex, f"Cannot create experiment '{exp_name}'")
        exp = mlflow_client.get_experiment_by_name(exp_name)
        _logger.info(f"Using existing experiment '{exp.name}' with location '{exp.artifact_location}'")
    return exp


def get_first_run(mlflow_client, exp_id_or_name):
    exp = get_experiment(mlflow_client, exp_id_or_name)
    runs = mlflow_client.search_runs(exp.experiment_id)
    return mlflow_client.get_run(runs[0].info.run_id)


def delete_experiment(mlflow_client, exp_id_or_name):
    exp = get_experiment(mlflow_client, exp_id_or_name)
    _logger.info(f"Deleting experiment: name={exp.name} experiment_id={exp.experiment_id}")
    mlflow_client.delete_experiment(exp.experiment_id)


def delete_model(mlflow_client, model_name):
    versions = SearchModelVersionsIterator(mlflow_client, filter=f"name='{model_name}'")
    _logger.info(f"Deleting model '{model_name}'")
    for vr in versions:
        if vr.current_stage == "None":
            mlflow_client.delete_model_version(model_name, vr.version)
    mlflow_client.delete_registered_model(model_name)


def get_last_run(mlflow_client, exp_id_or_name):
    exp = get_experiment(mlflow_client, exp_id_or_name)
    runs = mlflow_client.search_runs(exp.experiment_id, order_by=["attributes.start_time desc"], max_results=1)
    return runs[0]


def create_workspace_dir(dbx_client, workspace_dir):
    """
    Create Databricks workspace directory.
    """
    _logger.info(f"Creating Databricks workspace directory '{workspace_dir}'")
    dbx_client.post("workspace/mkdirs", { "path": workspace_dir })

# == Download artifact issue

def download_artifacts(client, download_uri, dst_path=None, fix=True):
    """ 
    Apparently the tracking_uri argument is not honored for mlflow.artifacts.download_artifacts().
    It seems that tracking_uri is ignored and the global mlflow.get_tracking_uri() is always used.
    If the two happen to be the same operation will succeed.
    If not, it fails.
    Issue: Merge pull request #104 from mingyu89/fix-download-artifacts
    """ 
    if fix:
        previous_tracking_uri = mlflow.get_tracking_uri()
        mlflow.set_tracking_uri(client._tracking_client.tracking_uri)
        local_path = mlflow.artifacts.download_artifacts(
            artifact_uri = download_uri,
            dst_path = dst_path,
        )
        mlflow.set_tracking_uri(previous_tracking_uri)
    else:
        local_path = mlflow.artifacts.download_artifacts(
            artifact_uri = download_uri,
            dst_path = dst_path,
            tracking_uri = client._tracking_client.tracking_uri
        )
    return local_path


# == Dump exception functions

def mk_msg_RestException(e):
    return { "RestException": { **e.json,  **{ "http_status_code": e.get_http_status_code()} } }


def dump_exception(ex, msg=""):
    from mlflow.exceptions import MlflowException
    if issubclass(ex.__class__,MlflowException):
        _dump_MlflowException(ex, msg)
    else:
        _dump_exception(ex, msg)


def _dump_exception(ex, msg=""):
    _logger.info(f"==== {ex.__class__.__name__}: {msg} =====")
    _logger.info(f"  type: {type(ex)}")
    _logger.info(f"  ex:   '{ex}'")
    _logger.info("  attrs:")
    for k,v in ex.__dict__.items():
        if isinstance(v,dict):
            _logger.info(f"    {k}:")
            for k2,v2 in v.items():
                _logger.info(f"      {k2}: {v2}")
        else:
            if k == "src_exception" and v:
                _logger.info(f"    {k}: {type(v)}")
            _logger.info(f"    {k}: {v}")


def _dump_MlflowException(ex, msg=""):
    _dump_exception(ex, msg)
    _logger.info(f"  get_http_status_code(): {ex.get_http_status_code()}")
    _logger.info(f"  serialize_as_json():    {ex.serialize_as_json()}") 
