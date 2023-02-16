import os
from mlflow.exceptions import RestException
from mlflow_export_import.common import MlflowExportImportException


def get_mlflow_host():
    """ Returns the host (tracking URI) and token """
    return get_mlflow_host_token()[0]


def get_mlflow_host_token():
    """ Returns the host (tracking URI) and token """

    uri = os.environ.get("MLFLOW_TRACKING_URI", None)
    if uri is not None and not uri.startswith("databricks"):
        return (uri, None)
    try:
        from mlflow_export_import.common import databricks_cli_utils
        toks = uri.split("//")
        profile = uri.split("//")[1] if len(toks) > 1 else None
        return databricks_cli_utils.get_host_token(profile)
    #except databricks_cli.utils.InvalidConfigurationError as e:
    except Exception as e: # TODO: make more specific
        print("WARNING:", e)
        return (None, None)


def get_experiment(mlflow_client, exp_id_or_name):
    """ Gets an experiment either by ID or name.  """
    exp = mlflow_client.get_experiment_by_name(exp_id_or_name)
    if exp is None:
        try:
            exp = mlflow_client.get_experiment(exp_id_or_name)
        except Exception:
            raise MlflowExportImportException(f"Cannot find experiment ID or name '{exp_id_or_name}'. Client: {mlflow_client}'")
    return exp


def set_experiment(mlflow_client, dbx_client, exp_name, tags=None):
    """
    Set experiment name. 
    For Databricks, create the workspace directory if it doesn't exist.
    :return: Experiment ID
    """
    from mlflow_export_import.common import utils
    if utils.importing_into_databricks():
        create_workspace_dir(dbx_client, os.path.dirname(exp_name))
    try:
        if not tags: tags = {}
        exp_id = mlflow_client.create_experiment(exp_name, tags=tags)
        exp = mlflow_client.get_experiment(exp_id)
        print(f"Created experiment '{exp.name}' with location '{exp.artifact_location}'")
    except RestException as ex:
        if ex.error_code != "RESOURCE_ALREADY_EXISTS":
            raise(ex)
        exp = mlflow_client.get_experiment_by_name(exp_name)
        print(f"Using existing experiment '{exp.name}' with location '{exp.artifact_location}'")
    return exp.experiment_id


def get_first_run(mlflow_client, exp_id_or_name):
    exp = get_experiment(mlflow_client, exp_id_or_name)
    runs = mlflow_client.search_runs(exp.experiment_id)
    return mlflow_client.get_run(runs[0].info.run_id)


def delete_experiment(mlflow_client, exp_id_or_name):
    exp = get_experiment(mlflow_client, exp_id_or_name)
    print(f"Deleting experiment: name={exp.name} experiment_id={exp.experiment_id}")
    mlflow_client.delete_experiment(exp.experiment_id)


def delete_model(mlflow_client, model_name):
    versions = mlflow_client.search_model_versions(f"name = '{model_name}'")
    print(f"Deleting {len(versions)} versions of model '{model_name}'")
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
    print(f"Creating Databricks workspace directory '{workspace_dir}'")
    dbx_client.post("workspace/mkdirs", { "path": workspace_dir })
