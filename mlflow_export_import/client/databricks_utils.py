from databricks_cli.sdk.api_client import ApiClient
from mlflow_export_import.client import mlflow_auth_utils


def get_api_client():
    (host, token) = mlflow_auth_utils.get_mlflow_host_token()
    return ApiClient(None, None, host, token)
