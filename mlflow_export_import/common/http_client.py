import os
import json
import requests
from mlflow_export_import.common import mlflow_utils
from mlflow_export_import.common import MlflowExportImportException

class HttpClient():
    """ Wrapper for get and post methods for Databricks REST APIs. """
    def __init__(self, api_name, host=None, token=None):
        self.api_uri = "?"
        if host is None:
            (host,token) = mlflow_utils.get_mlflow_host_token()
            if host is None:
                raise MlflowExportImportException("MLflow host or token is not configured correctly")
        self.api_uri = os.path.join(host,api_name)
        self.token = token

    def _get(self, resource):
        """ Executes an HTTP GET call
        :param resource: Relative path name of resource such as cluster/list
        """
        uri = self._mk_uri(resource)
        rsp = requests.get(uri, headers=self._mk_headers())
        self._check_response(rsp, uri)
        return rsp

    def get(self, resource):
        return json.loads(self._get(resource).text)

    def post(self, resource, data):
        """ Executes an HTTP POST call
        :param resource: Relative path name of resource such as runs/search
        :param data: Post request payload
        """
        uri = self._mk_uri(resource)
        data=json.dumps(data)
        rsp = requests.post(uri, headers=self._mk_headers(), data=data)
        self._check_response(rsp,uri)
        return json.loads(rsp.text)

    def _mk_headers(self):
        return {} if self.token is None else { "Authorization": f"Bearer {self.token}" }

    def _mk_uri(self, resource):
        return f"{self.api_uri}/{resource}"

    def _check_response(self, rsp, uri):
        if rsp.status_code < 200 or rsp.status_code > 299:
            raise MlflowExportImportException(f"HTTP status code: {rsp.status_code}. Reason: {rsp.reason} URL: {uri}")

    def __repr__(self): 
        return self.api_uri

class DatabricksHttpClient(HttpClient):
    def __init__(self, host=None, token=None):
        super().__init__("api/2.0", host, token)

class MlflowHttpClient(HttpClient):
    def __init__(self, host=None, token=None):
        super().__init__("api/2.0/mlflow", host, token)
