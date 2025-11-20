from abc import abstractmethod, ABCMeta
import os
import json
from requests.auth import HTTPBasicAuth
import requests
import click
from mlflow_export_import.common import MlflowExportImportException
from . import USER_AGENT
from . import mlflow_auth_utils
from . import databricks_cli_utils

_TIMEOUT = 120 # per mlflow.MlflowClient


class BaseHttpClient(metaclass=ABCMeta):
    """
    Base HTTP client class.
    """

    @abstractmethod
    def get(self, resource, params=None):
        pass

    @abstractmethod
    def _get(self, resource, params=None):
        pass


    @abstractmethod
    def post(self, resource, data=None):
        pass

    @abstractmethod
    def _post(self, resource, data=None):
        pass


    @abstractmethod
    def put(self, resource, data=None):
        pass

    @abstractmethod
    def _put(self, resource, data=None):
        pass


    @abstractmethod
    def patch(self, resource, data=None):
        pass

    @abstractmethod
    def _patch(self, resource, data=None):
        pass


    @abstractmethod
    def delete(self, resource):
        pass

    @abstractmethod
    def _delete(self, resource):
        pass


    @abstractmethod
    def get_api_uri(self):
        pass

    @abstractmethod
    def get_token(self):
        pass


class HttpClient(BaseHttpClient):
    """
    Wrapper for HTTP calls for MLflow Databricks APIs.
    """
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
                http_status_code=401
            )
        self.host = host
        self.api_uri = os.path.join(host, api_name)
        self.token = token
        user = os.environ.get("MLFLOW_TRACKING_USERNAME")
        password = os.environ.get("MLFLOW_TRACKING_PASSWORD")
        self.auth = HTTPBasicAuth(user, password) if user and password else None


    def _get(self, resource, params=None):
        uri = self._mk_uri(resource)
        rsp = requests.get(uri, headers=self._mk_headers(), data=params, auth=self.auth, timeout=_TIMEOUT)
        return self._check_response(rsp, params)


    def get(self, resource, params=None):
        """ Executes an HTTP GET call
        :param resource: Relative path name of resource such as experiments/search
        :param params: Dict of query parameters
        """
        rsp = self._get(resource, self._json_dumps(params))
        return self._json_loads(rsp, params)


    def _post(self, resource, data=None):
        return self._mutator(requests.post, resource, data)

    def post(self, resource, data=None):
        """ Executes an HTTP POST call
        :param resource: Relative path name of resource such as runs/search
        :param data: Request payload as dict
        """
        rsp = self._post(resource, self._json_dumps(data))
        return self._json_loads(rsp, data)


    def _put(self, resource, data=None):
        return self._mutator(requests.put, resource, data)

    def put(self, resource, data=None):
        """ Executes an HTTP PUT call
        :param resource: Relative path name of resource
        :param data: Request payload as dict
        """
        rsp = self._put(resource, self._json_dumps(data))
        return self._json_loads(rsp, data)


    def _patch(self, resource, data=None):
        return self._mutator(requests.patch, resource, data)

    def patch(self, resource, data=None):
        """ Executes an HTTP PATCH call
        :param resource: Relative path name of resource
        :param data: Request payload as dict
        """
        rsp = self._patch(resource, self._json_dumps(data))
        return self._json_loads(rsp, data)


    def _delete(self, resource):
        uri = self._mk_uri(resource)
        rsp = requests.delete(uri, headers=self._mk_headers(), auth=self.auth, timeout=_TIMEOUT)
        return self._check_response(rsp)

    def delete(self, resource):
        """ Executes an HTTP POST call
        :param resource: Relative path name of resource such as runs/search
        """
        return json.loads(self._delete(resource).text)


    def _mutator(self, method, resource, data=None):
        uri = self._mk_uri(resource)
        rsp = method(uri, headers=self._mk_headers(), data=data, auth=self.auth, timeout=_TIMEOUT)
        return self._check_response(rsp)


    def get_api_uri(self):
        return self.api_uri

    def get_token(self):
        return self.token


    def _json_dumps(self, data):
        return json.dumps(data) if data else None

    def _mk_headers(self):
        headers = { "User-Agent": USER_AGENT, "Content-Type": "application/json" }
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
            msg = { "http_status_code": rsp.status_code, "uri": rsp.url, "params": params, "response": rsp.text }
            raise MlflowExportImportException(json.dumps(msg), http_status_code = rsp.status_code)
        return rsp

    def _json_loads(self, rsp, params):
        json_str = rsp.text
        try:
            return json.loads(json_str)
        except json.decoder.JSONDecodeError as e:
            import traceback
            traceback.print_exc()
            msg = {
                "uri": rsp.url,
                "method": rsp.request.method,
                "params": params,
                "exception": str(e),
                "response": json_str
            }
            raise MlflowExportImportException(msg, http_status_code=rsp.status_code)

    def __repr__(self):
        return self.api_uri


class DatabricksHttpClient(HttpClient):
    """
    Databricks API client: api/2.0
    """
    def __init__(self, host=None, token=None):
        super().__init__("api/2.0", host, token)


class MlflowHttpClient(HttpClient):
    """
    MLflow API client: api/2.0
    """
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
    print("Options:")
    for k,v in locals().items():
        print(f"  {k}: {v}")

    def _write_output(rsp, output_file):
        json_str = json.dumps(json.loads(rsp.text), indent=2)
        print(json_str)
        if output_file:
            print(f"Output file: {output_file}")
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
        rsp = client._get(resource, _get_params(params))
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
        print(f"ERROR: Unsupported HTTP method '{method}'")


if __name__ == "__main__":
    main()
