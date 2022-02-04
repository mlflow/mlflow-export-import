import os
import json
import requests
import click
from mlflow_export_import.common import mlflow_utils
from mlflow_export_import.common import MlflowExportImportException
from mlflow_export_import.common import USER_AGENT

class HttpClient():
    """ Wrapper for GET and POST methods for Databricks REST APIs  - standard Databricks API and MLflow API. """
    def __init__(self, api_name, host=None, token=None):
        """
        :param api_name: Name of base API such as 'api/2.0' or 'api/2.0/mlflow'.
        :param host: Host name of tracking server.
        :param token: Databricks token.
        """
        self.api_uri = "?"
        if host is None:
            (host,token) = mlflow_utils.get_mlflow_host_token()
            if host is None:
                raise MlflowExportImportException("MLflow host or token is not configured correctly")
        self.api_uri = os.path.join(host,api_name)
        self.token = token

    def _get(self, resource, params=None):
        """ Executes an HTTP GET call
        :param resource: Relative path name of resource such as cluster/list
        :param params: Dict of query parameters 
        """
        uri = self._mk_uri(resource)
        rsp = requests.get(uri, headers=self._mk_headers(), json=params)
        self._check_response(rsp, uri, params)
        return rsp

    def get(self, resource, params=None):
        return json.loads(self._get(resource, params).text)

    def _post(self, resource, data):
        """ Executes an HTTP POST call
        :param resource: Relative path name of resource such as runs/search
        :param data: Post request payload
        """
        uri = self._mk_uri(resource)
        data = json.dumps(data)
        rsp = requests.post(uri, headers=self._mk_headers(), data=data)
        self._check_response(rsp,uri)
        return rsp

    def post(self, resource, data):
        return json.loads(self._post(resource, data).text)

    def _mk_headers(self):
        headers = { "User-Agent": USER_AGENT }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}" 
        return headers

    def _mk_uri(self, resource):
        return f"{self.api_uri}/{resource}"

    def _check_response(self, rsp, uri, params=None):
        if rsp.status_code < 200 or rsp.status_code > 299:
            raise MlflowExportImportException(f"HTTP status code: {rsp.status_code}. Reason: {rsp.reason}. URI: {uri}. Params: {params}.")

    def __repr__(self): 
        return self.api_uri

class DatabricksHttpClient(HttpClient):
    def __init__(self, host=None, token=None):
        super().__init__("api/2.0", host, token)

class MlflowHttpClient(HttpClient):
    def __init__(self, host=None, token=None):
        super().__init__("api/2.0/mlflow", host, token)


@click.command()
@click.option("--api", help="API: mlflow|databricks.", default="mlflow", type=str)
@click.option("--resource", help="API resource such as 'experiments/list'.", required=True, type=str)
@click.option("--method", help="HTTP method: GET|POST.", default="GET", type=str)
@click.option("--params", help="HTTP GET query parameters as JSON.", required=False, type=str)
@click.option("--data", help="HTTP POST data as JSON.", required=False, type=str)
@click.option("--output-file", help="Output file.", required=False, type=str)
@click.option("--verbose", help="Verbose.", type=bool, default=False, show_default=True)

def main(api, resource, method, params, data, output_file, verbose):
    def write_output(rsp, output_file):
        if output_file:
            print(f"Output file: {output_file}")
            with open(output_file, "w") as f:
                f.write(rsp.text)
        else:
            print(rsp.text)

    if verbose:
        print("Options:")
        for k,v in locals().items():
            print(f"  {k}: {v}")

    client = DatabricksHttpClient() if api == "databricks" else MlflowHttpClient()
    method = method.upper() 
    if "GET" == method:
        if params:
            params = json.loads(params)
        rsp = client._get(resource, params)
        write_output(rsp, output_file)
    elif "POST" == method:
        rsp = client._post(resource, data)
        write_output(rsp, output_file)
    else:
        print(f"ERROR: Unsupported HTTP method '{method}'")

if __name__ == "__main__":
    main()
