"""
Utilities
"""

from databricks_cli.sdk.api_client import ApiClient
import cred_utils


def get_api_client(profile=None):
    (host,token) = cred_utils.get_credentials(profile)
    return ApiClient(None, None, host, token)
