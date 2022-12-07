import os
import json
import mlflow


def  create_client(uri):
    return mlflow.tracking.MlflowClient() if uri is None else mlflow.tracking.MlflowClient(uri)


# monkey patch mlflow.tracking.MlflowClient to return tracking URI in __repr__

def add_repr_to_MlflowClient():
    def custom_repr(self): 
        try:
            return self._tracking_client.tracking_uri
        except AttributeError:
            return "tracking_uri??"
    mlflow.tracking.MlflowClient.__repr__ = custom_repr


add_repr_to_MlflowClient()
