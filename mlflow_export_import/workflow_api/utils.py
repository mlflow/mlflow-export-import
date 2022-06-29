import json
from mlflow_export_import.workflow_api import cred_utils, log_utils

from databricks_cli.sdk.api_client import ApiClient

def get_api_client(profile=None):
    (host,token) = cred_utils.get_credentials(profile)
    print("Host:",host)
    return ApiClient(None, None, host, token)

def load_json_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.loads(f.read())

def dump_as_json(msg, dct):
    print(f"{msg}:")
    print(json.dumps(dct,indent=2)+"\n")
