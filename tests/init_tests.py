import os
import pytest
import tempfile
from collections import namedtuple
import mlflow

print("mlflow.tracking_uri:",mlflow.tracking.get_tracking_uri())

uri_src = os.environ.get("MLFLOW_TRACKING_URI_SRC",None)
assert uri_src
print("MLFLOW_TRACKING_URI_SRC:",uri_src)
client_src = mlflow.tracking.MlflowClient(uri_src)
print("client_src:",client_src)

uri_dst = os.environ.get("MLFLOW_TRACKING_URI_DST",None)
assert uri_dst
print("MLFLOW_TRACKING_URI_DST:",uri_dst)
client_dst = mlflow.tracking.MlflowClient(uri_dst)
print("client_dst:",client_dst)

MlflowServer = namedtuple(
    "MlflowServer",
    ["client_src", "client_dst", "output_dir"]
)

@pytest.fixture(scope="session")
def mlflow_server():
    with tempfile.TemporaryDirectory() as tmpdir:
        assert mlflow.get_tracking_uri() is not None
        yield MlflowServer(
            client_src, client_dst, tmpdir
        )
