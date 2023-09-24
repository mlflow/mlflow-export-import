from typing import Any
import os
import pytest
import mlflow
from dataclasses import dataclass

from mlflow_export_import.common import utils
from mlflow_export_import.common import MlflowExportImportException
from mlflow_export_import.client.http_client import DatabricksHttpClient
from tests import utils_test

_logger = utils.getLogger(__name__)


class Dict2Class():
    def __init__(self, dct):
        self.dct = dct
        for k,v in dct.items():
            if isinstance(v,dict):
                v = Dict2Class(v)
            setattr(self, k, v)
    def __str__(self):
        return str(self.dct)

_cfg = utils_test.read_config_file()
cfg = Dict2Class(_cfg)


class Workspace():
    def __init__(self, cfg_ws):
        self.cfg_ws = cfg_ws
        self.base_dir = cfg_ws.base_dir
        self.mlflow_client = mlflow.MlflowClient(cfg_ws.profile)
        self.dbx_client = DatabricksHttpClient(self.mlflow_client.tracking_uri)

        _logger.info(f"base_dir: {self.base_dir}")
        _logger.info(f"mlflow_client: {self.mlflow_client}")
        _logger.info(f"dbx_client: {self.dbx_client}")

    def __repr__(self):
        return str({ k:v for k,v in self.__dict__.items() })

workspace_src =  Workspace(cfg.workspace_src)
workspace_dst =  Workspace(cfg.workspace_dst)

utils.importing_into_databricks(workspace_dst.dbx_client)


def init_tests():
    _init_workspace(workspace_src)
    _init_workspace(workspace_dst)

def _init_workspace(ws):
    _delete_directory(ws)
    _create_base_dir(ws)


def _create_base_dir(ws):
    """ Create test base directory """
    params = { "path": ws.base_dir }
    _logger.info(f"{ws.dbx_client}: Creating {ws.base_dir}")
    ws.dbx_client.post("workspace/mkdirs", params)

def _delete_directory(ws):
    """ Deletes notebooks in test based directory """
    params = { "path": ws.base_dir, "recursive": True }
    _logger.info(f"{ws.dbx_client}: Deleting {ws.base_dir}")
    try:
        ws.dbx_client.post("workspace/delete", params)
    except MlflowExportImportException as e:
        _logger.warning(f"Delete workspace API call: {e}")


@dataclass()
class TestContext:
    mlflow_client_src: Any
    mlflow_client_dst: Any
    dbx_client_src: Any
    dbx_client_dst: Any
    output_dir: str
    output_run_dir: str


@pytest.fixture(scope="session")
def test_context():
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        assert mlflow.get_tracking_uri() is not None
        output_dir = os.environ.get("MLFLOW_EXPORT_IMPORT_OUTPUT_DIR",None) # for debugging
        if output_dir:
            utils_test.create_output_dir(output_dir)
        else:
            output_dir = tmpdir
        yield TestContext(
            workspace_src.mlflow_client, 
            workspace_dst.mlflow_client, 
            workspace_src.dbx_client, 
            workspace_dst.dbx_client, 
            output_dir, 
            os.path.join(output_dir,"run")
        )


# Initialize the testing world
init_tests()
