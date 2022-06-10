import os
import mlflow
from mlflow_export_import.common import MlflowExportImportException

def dump_mlflow_info():
    print("MLflow Info:")
    print("  MLflow Version:", mlflow.version.VERSION)
    print("  Tracking URI:", mlflow.tracking.get_tracking_uri())
    mlflow_host = get_mlflow_host()
    print("  Real MLflow host:", mlflow_host)
    print("  MLFLOW_TRACKING_URI:", os.environ.get("MLFLOW_TRACKING_URI",""))
    print("  DATABRICKS_HOST:", os.environ.get("DATABRICKS_HOST",""))
    print("  DATABRICKS_TOKEN:", os.environ.get("DATABRICKS_TOKEN",""))

def get_mlflow_host():
    """ Returns the host (tracking URI) and token """
    return get_mlflow_host_token()[0]

def get_mlflow_host_token():
    """ Returns the host (tracking URI) and token """
    uri = os.environ.get("MLFLOW_TRACKING_URI",None)
    if uri is not None and uri != "databricks":
        return (uri,None)
    try:
        from mlflow_export_import.common import databricks_cli_utils
        profile = os.environ.get("MLFLOW_PROFILE",None)
        return databricks_cli_utils.get_host_token(profile)
    #except databricks_cli.utils.InvalidConfigurationError as e:
    except Exception as e: # TODO: make more specific
        print("WARNING:",e)
        return (None,None)

def get_experiment(mlflow_client, exp_id_or_name):
    """ Gets an experiment either by ID or name.  """
    exp = mlflow_client.get_experiment_by_name(exp_id_or_name)
    if exp is None:
        try:
            exp = mlflow_client.get_experiment(exp_id_or_name)
        except Exception:
            raise MlflowExportImportException(f"Cannot find experiment ID or name '{exp_id_or_name}'. Client: {mlflow_client}'")
    return exp

def create_workspace_dir(dbx_client, workspace_dir):
    """
    Create Databricks workspace directory.
    """
    print(f"Creating Databricks workspace directory '{workspace_dir}'")
    dbx_client.post("workspace/mkdirs", { "path": workspace_dir })

def set_experiment(mlflow_client, dbx_client, exp_name):
    """
    Set experiment name. 
    For Databricks, create the workspace directory if it doesn't exist.
    :return: Experiment ID
    """
    from mlflow_export_import import utils
    if utils.importing_into_databricks():
        create_workspace_dir(dbx_client, os.path.dirname(exp_name))
    try:
        return mlflow_client.create_experiment(exp_name)
    except Exception:
        exp = mlflow_client.get_experiment_by_name(exp_name)
        return exp.experiment_id


# BUG
def _get_experiment(mlflow_client, exp_id_or_name):
    try:
        exp = mlflow_client.get_experiment(exp_id_or_name)
    except Exception:
        exp = mlflow_client.get_experiment_by_name(exp_id_or_name)
    if exp is None:
        raise MlflowExportImportException(f"Cannot find experiment ID or name '{exp_id_or_name}'. Client: {mlflow_client}'")
    return exp
