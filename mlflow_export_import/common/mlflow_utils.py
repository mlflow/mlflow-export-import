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
        except Exception as ex:
            raise MlflowExportImportException(ex, f"Cannot find experiment ID or name '{exp_id_or_name}'. Client: {mlflow_client}'")
    return exp



def set_experiment(mlflow_client, dbx_client, exp_name, tags=None, is_create_new_exp=False):
    """
    Set experiment name. 
    For Databricks, create the workspace directory if it doesn't exist.
    :return: Experiment ID
    """
    from mlflow_export_import.common import utils
    if utils.importing_into_databricks():
        create_workspace_dir(dbx_client, os.path.dirname(exp_name))

    if not tags: tags = {}
    tags = utils.create_mlflow_tags_for_databricks_import(tags)
    
    if is_create_new_exp:
        exp_id = mlflow_client.create_experiment(exp_name, tags=tags)
        exp = mlflow_client.get_experiment(exp_id)
    else:
        exp = mlflow_client.get_experiment_by_name(exp_name)

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


# == Dump exception functions


def dump_exception(ex, msg=""):
    from mlflow.exceptions import MlflowException
    if issubclass(ex.__class__,MlflowException):
        _dump_MlflowException(ex, msg)
    else:
        _dump_exception(ex, msg)

def _dump_exception(ex, msg=""):
    print(f"==== {ex.__class__.__name__}: {msg} =====")
    print(f"  type: {type(ex)}")
    print(f"  ex:   '{ex}'")
    print(f"  attrs:")
    for k,v in ex.__dict__.items():
        print(f"    {k}: {v}")


def _dump_MlflowException(ex, msg=""):
    _dump_exception(ex, msg)
    print(f"  get_http_status_code(): {ex.get_http_status_code()}")
    print(f"  serialize_as_json():    {ex.serialize_as_json()}") 
