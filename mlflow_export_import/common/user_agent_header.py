"""
Set User-Agent header as 'mlflow-export-import/1.0.0'.
"""

from mlflow.tracking.request_header.abstract_request_header_provider import RequestHeaderProvider

_user_agent = "mlflow-export-import/1.0.0"

class MlflowExportImportRequestHeaderProvider(RequestHeaderProvider):
    def __init(self):
        pass
    def in_context(self):
        return True
    def request_headers(self):
        return { "User-Agent": _user_agent }
