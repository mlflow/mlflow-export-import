import os
import mlflow

def dump_mlflow_info():
    print("MLflow Info:")
    print("  MLflow Version:", mlflow.version.VERSION)
    print("  Tracking URI:", mlflow.tracking.get_tracking_uri())
    mlflow_host = get_mlflow_host()
    print("  Real MLflow host:", mlflow_host)
    print("  MLFLOW_TRACKING_URI:", os.environ.get("MLFLOW_TRACKING_URI",""))
    print("  DATABRICKS_HOST:", os.environ.get("DATABRICKS_HOST",""))
    print("  DATABRICKS_TOKEN:", os.environ.get("DATABRICKS_TOKEN",""))

''' Returns the host (tracking URI) and token '''
def get_mlflow_host():
    return get_mlflow_host_token()[0]

''' Returns the host (tracking URI) and token '''
def get_mlflow_host_token():
    uri = os.environ.get('MLFLOW_TRACKING_URI',None)
    if uri is not None and uri != "databricks":
        return (uri,None)
    try:
        from mlflow_export_import.common import databricks_cli_utils
        profile = os.environ.get('MLFLOW_PROFILE',None)
        host_token = databricks_cli_utils.get_host_token(profile)
        return databricks_cli_utils.get_host_token(profile)
    #except databricks_cli.utils.InvalidConfigurationError as e:
    except Exception as e: # TODO: make more specific
        #import traceback
        #traceback.print_exc()
        print("WARNING:",e)
        return (None,None)

'''
Gets an experiment either by ID or name.
'''
def get_experiment(client, exp_id_or_name):
    exp = client.get_experiment_by_name(exp_id_or_name)
    if exp is None:
        try:
            exp = client.get_experiment(exp_id_or_name)
        except Exception as e:
             raise Exception(f"Cannot find experiment ID or name '{exp_id_or_name}'. Client: {client}'")
    return exp

# BUG
def _get_experiment(client, exp_id_or_name):
    try:
        exp = client.get_experiment(exp_id_or_name)
    except Exception as e:
        exp = client.get_experiment_by_name(exp_id_or_name)
    if exp is None:
         raise Exception(f"Cannot find experiment ID or name '{exp_id_or_name}'. Client: {client}'")
    return exp
