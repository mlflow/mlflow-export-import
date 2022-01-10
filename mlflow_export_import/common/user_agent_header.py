"""
Set HTTP User-Agent header as 'mlflow-export-import/1.X.X' for MLflow client.
"""

from mlflow.tracking.request_header.abstract_request_header_provider import RequestHeaderProvider
from mlflow_export_import.common import USER_AGENT

class MlflowExportImportRequestHeaderProvider(RequestHeaderProvider):
    def __init(self):
        pass
    def in_context(self):
        return True
    def request_headers(self):
        return { "User-Agent": USER_AGENT }
