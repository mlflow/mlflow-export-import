"""
Utilities
"""

from databricks_cli.sdk.api_client import ApiClient
import cred_utils


def get_api_client(profile=None):
    (host,token) = cred_utils.get_credentials(profile)
    return ApiClient(None, None, host, token)


def read_config_file():
    import yaml
    path = "config.yaml"
    with open(path,  encoding="utf-8") as f:
        dct = yaml.safe_load(f)
        print("Config:")
        for k,v in dct.items():
            print(f"  {k}: {v}")
    return dct
