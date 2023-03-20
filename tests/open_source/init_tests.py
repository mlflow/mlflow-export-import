import os
import pytest
import tempfile
from collections import namedtuple
import mlflow
import utils_test

from mlflow_export_import.common import utils
_logger = utils.getLogger(__name__)

_logger.info(f"mlflow.tracking_uri {mlflow.tracking.get_tracking_uri()}")

uri_src = os.environ.get("MLFLOW_TRACKING_URI_SRC",None)
_logger.info(f"MLFLOW_TRACKING_URI_SRC: {uri_src}")
assert uri_src,"Environment variable MLFLOW_TRACKING_URI_SRC must be set"
client_src = mlflow.tracking.MlflowClient(uri_src)
_logger.info(f"client_src: {client_src}")

uri_dst = os.environ.get("MLFLOW_TRACKING_URI_DST",None)
_logger.info(f"MLFLOW_TRACKING_URI_DST: {uri_dst}")
assert uri_dst
client_dst = mlflow.tracking.MlflowClient(uri_dst)
_logger.info(f"client_dst: {client_dst}")

MlflowContext = namedtuple(
    "MlflowContext",
    ["client_src", "client_dst", "output_dir", "output_run_dir"]
)

@pytest.fixture(scope="session")
def mlflow_context():
    with tempfile.TemporaryDirectory() as tmpdir:
        assert mlflow.get_tracking_uri() is not None
        output_dir = os.environ.get("MLFLOW_EXPORT_IMPORT_OUTPUT_DIR",None) # for debugging
        if output_dir:
            utils_test.create_output_dir(output_dir)
        else:
            output_dir = tmpdir
        yield MlflowContext(
            client_src, client_dst, output_dir, os.path.join(output_dir,"run")
        )
