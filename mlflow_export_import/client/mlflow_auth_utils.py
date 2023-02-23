import os
from mlflow_export_import.client import databricks_cli_utils


def get_mlflow_host():
    """ Returns the host (tracking URI) and token """
    return get_mlflow_host_token()[0]


def get_mlflow_host_token():
    """ Returns the host (tracking URI) and token """

    uri = os.environ.get("MLFLOW_TRACKING_URI", None)
    if uri is not None and not uri.startswith("databricks"):
        return (uri, None)
    try:
        toks = uri.split("//")
        profile = uri.split("//")[1] if len(toks) > 1 else None
        return databricks_cli_utils.get_host_token(profile)
    # databricks_cli.utils.InvalidConfigurationError 
    # requests.exceptions.InvalidSchema(f"No connection adapters were found for {url!r}")
    except Exception as e: 
        print("WARNING:", e)
        return (None, None)
