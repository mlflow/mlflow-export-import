import os
import json
import requests
import click
from mlflow_export_import.common import utils
from mlflow_export_import.common import MlflowExportImportException
from mlflow_export_import.client import USER_AGENT
from mlflow_export_import.client import mlflow_auth_utils
from mlflow_export_import.client import databricks_cli_utils

_logger = utils.getLogger(__name__)
_TIMEOUT = 15


class HttpClient():
    """ Wrapper for GET and POST methods for Databricks REST APIs  - standard Databricks API and MLflow API. """
    def __init__(self, api_name, host=None, token=None):
        """
        :param api_name: Name of base API such as 'api/2.0' or 'api/2.0/mlflow'.
        :param host: Host name of tracking server such as 'http://localhost:5000' or 'databricks://my_profile'.
        :param token: Databricks token if using Databricks.
        """

        if host:
            # Assume 'host' is a Databricks profile 
            if not host.startswith("http"):
                profile = host.replace("databricks://","")
                (host, token) = databricks_cli_utils.get_host_token_for_profile(profile)
        else:
            (host, token) = mlflow_auth_utils.get_mlflow_host_token()

        if host is None:
            raise MlflowExportImportException(
                "MLflow tracking URI (MLFLOW_TRACKING_URI environment variable) is not configured correctly",
                http_status_code=401)

        self.host = host
        self.api_uri = os.path.join(host, api_name)
        self.token = token
        

    def _get(self, resource, params=None):
        uri = self._mk_uri(resource)
        rsp = requests.get(uri, headers=self._mk_headers(), json=params, timeout=_TIMEOUT)
        return self._check_response(rsp, params)

    def get(self, resource, params=None):
        """ Executes an HTTP GET call
        :param resource: Relative path name of resource such as cluster/list
        :param params: Dict of query parameters
        """
        return json.loads(self._get(resource, params).text)


    def _post(self, resource, data=None):
        """ Executes an HTTP POST call
        :param resource: Relative path name of resource such as runs/search
        :param data: Request request payload as dict
        """
        return self._mutator(requests.post, resource, data)

    def post(self, resource, data=None):
        return json.loads(self._post(resource, self._json_dumps(data)).text)


    def _put(self, resource, data=None):
        return self._mutator(requests.put, resource, data)

    def put(self, resource, data=None):
        """ Executes an HTTP PUT call
        :param resource: Relative path name of resource
        :param data: Request payload as dict
        """
        return json.loads(self._put(resource, self._json_dumps(data)).text)

    def _json_dumps(self, data):
        return json.dumps(data) if data else None


    def _patch(self, resource, data=None):
        return self._mutator(requests.patch, resource, data)

    def patch(self, resource, data=None):
        """ Executes an HTTP PATCH call
        :param resource: Relative path name of resource
        :param data: Request payload as dict
        """
        return json.loads(self._patch(resource, self._json_dumps(data)).text)


    def _mutator(self, method, resource, data=None):
        uri = self._mk_uri(resource)
        rsp = method(uri, headers=self._mk_headers(), data=data, timeout=_TIMEOUT)
        return self._check_response(rsp)

    def _to_json(self, data):
        return json.dumps(data) if data else None

    def _delete(self, resource):
        uri = self._mk_uri(resource)
        rsp = requests.delete(uri, headers=self._mk_headers(), timeout=_TIMEOUT)
        return self._check_response(rsp)

    def delete(self, resource):
        """ Executes an HTTP POST call
        :param resource: Relative path name of resource such as runs/search
        :param data: Post request payload as dict
        """
        return json.loads(self._delete(resource).text)


    def _mk_headers(self):
        headers = { "User-Agent": USER_AGENT }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _mk_uri(self, resource):
        return f"{self.api_uri}/{resource}"

    def _get_response_text(self, rsp):
        try:
            return rsp.json()
        except requests.exceptions.JSONDecodeError:
            return rsp.text

    def _check_response(self, rsp, params=None):
        if rsp.status_code < 200 or rsp.status_code > 299:
            raise MlflowExportImportException(
               rsp.reason,
               http_status_code = rsp.status_code,
               http_reason = rsp.reason,
               http_method = rsp.request.method,
               uri = rsp.url,
               params = params,
               text = self._get_response_text(rsp)
            )
        return rsp

    def __repr__(self):
        return self.api_uri


class DatabricksHttpClient(HttpClient):
    def __init__(self, host=None, token=None):
        super().__init__("api/2.0", host, token)


class MlflowHttpClient(HttpClient):
    def __init__(self, host=None, token=None):
        super().__init__("api/2.0/mlflow", host, token)


@click.command()
@click.option("--api",
    help="API: mlflow|databricks.",
    type=str,
    default="mlflow",
)
@click.option("--resource",
    help="API resource such as 'experiments/search'.",
    type=str,
    required=True
)
@click.option("--method",
    help="HTTP method: GET|POST|PUT|PATCH|DELETE.",
    type=str,
    default="GET"
)
@click.option("--params",
    help="HTTP GET query parameters as JSON.",
    type=str,
    required=False
)
@click.option("--data",
    help="HTTP request entity body as JSON (for POST, PUT and PATCH).",
    type=str,
    required=False
)
@click.option("--output-file",
    help="Output file.",
    type=str,
    required=False
)
def main(api, resource, method, params, data, output_file):
    _logger.info("Options:")
    for k,v in locals().items():
        _logger.info(f"  {k}: {v}")

    def _write_output(rsp, output_file):
        json_str = json.dumps(json.loads(rsp.text), indent=2)
        print(json_str)
        if output_file:
            _logger.info(f"Output file: {output_file}")
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(json_str)

    def _get_params(params):
        if not params:
            return params
        if params.startswith("@"): # curl --data convention
            with open(params[1:], "r", encoding="utf-8") as f:
                return f.read()
        else:
            return params

    client = DatabricksHttpClient() if api == "databricks" else MlflowHttpClient()
    method = method.upper()
    if "GET" == method:
        if params:
            params = json.loads(params)
        rsp = client._get(resource, params)
        _write_output(rsp, output_file)
    elif "POST" == method:
        rsp = client._post(resource, _get_params(data))
        _write_output(rsp, output_file)
    elif "PUT" == method:
        rsp = client._put(resource, _get_params(data))
        _write_output(rsp, output_file)
    elif "PATCH" == method:
        data = _get_params(data)
        rsp = client._patch(resource, _get_params(data))
        _write_output(rsp, output_file)
    else:
        _logger.error(f"Unsupported HTTP method '{method}'")


if __name__ == "__main__":
    main()
