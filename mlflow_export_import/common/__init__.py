from mlflow.exceptions import MlflowException
import json

class MlflowExportImportException(Exception):
    DEFAULT_HTTP_STATUS_CODE = -1

    def __init__(self, ex, message=None, http_status_code=DEFAULT_HTTP_STATUS_CODE, **kwargs):
        self.message = str(ex) # if arg 'message' is not None else is src_exception's message
        self.src_message = None # message from source exception if arg 'message' is not None
        self.src_exception = None # source exception if exists
        self.http_status_code = http_status_code
        custom_kwargs = {}
        if issubclass(ex.__class__,Exception):
            self.src_exception = ex 
            if issubclass(ex.__class__,MlflowException):
                self.http_status_code = ex.get_http_status_code()
                custom_kwargs = { "mlflow_error_code":  ex.error_code }
            if message:
                self.message = message
                self.src_message = str(ex)

        self.kwargs = { "message": self.message, "http_status_code": self.http_status_code }
        self.kwargs = {**self.kwargs, **kwargs, **custom_kwargs}
        if self.src_message:
            self.kwargs["src_message"] = self.src_message
    
    def _add(self, dct, k, v):
        if v: dct[k] = v

    def __str__(self):
        return json.dumps(self.kwargs)
