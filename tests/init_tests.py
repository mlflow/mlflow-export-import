import pytest
import tempfile
from collections import namedtuple
import mlflow

print("mlflow.tracking_uri:",mlflow.tracking.get_tracking_uri())

MlflowServer = namedtuple(
    "MlflowServer",
    ["client", "output_dir"]
)

@pytest.fixture(scope="session")
def mlflow_server():
    with tempfile.TemporaryDirectory() as tmpdir:
        assert mlflow.get_tracking_uri() is not None
        client = mlflow.tracking.MlflowClient()
        yield MlflowServer(
            client, tmpdir
        )
