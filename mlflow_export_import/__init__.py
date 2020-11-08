
import os
import json
import mlflow

class BaseCopier():
    def __init__(self, src_client, dst_client):
        self.src_client = src_client
        self.dst_client = dst_client

    def get_experiment(self, client, exp_name):
        exp = client.get_experiment_by_name(exp_name)
        if exp is None:
            exp_id = client.create_experiment(exp_name)
            exp = client.get_experiment(exp_id)
        return exp

def mk_dbfs_path(path):
    return path.replace("/dbfs","dbfs:")

def mk_local_path(path):
    return path.replace("dbfs:","/dbfs")

def peek_at_experiment(exp_dir):
    manifest_path = os.path.join(exp_dir,"manifest.json")
    with open(mk_local_path(manifest_path), "r") as f:
        content = f.read()
    print("manifest path:",manifest_path)
    print(content)

def  create_client(uri):
    return mlflow.tracking.MlflowClient() if uri is None else mlflow.tracking.MlflowClient(uri)

# monkey patch mlflow.tracking.MlflowClient

def add_repr_to_MlflowClient():
    def custom_repr(self): 
        try:
            return self._tracking_client.tracking_uri
        except AttributeError:
            return "tracking_uri??"
    mlflow.tracking.MlflowClient.__repr__ = custom_repr

add_repr_to_MlflowClient()
