import os
import json
import mlflow
from mlflow_export_import import version

__version__ = version.__version__

# monkey patch mlflow.tracking.MlflowClient to return tracking URI in __repr__

def add_repr_to_MlflowClient():
    def custom_repr(self):
        try:
            msg = { "tracking_uri": self.tracking_uri, "registry_uri": self._registry_uri }
        except AttributeError as e:
            msg = { "error": str(e) }
        return json.dumps(msg)
    mlflow.client.MlflowClient.__repr__ = custom_repr


add_repr_to_MlflowClient()
