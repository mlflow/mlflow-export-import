from collections import namedtuple
import pytest
import tempfile
import mlflow
from databricks_tester import DatabricksTester
import utils
import utils_test

cfg = utils.read_config_file()
profile = cfg.get("profile", None)
tester = DatabricksTester(
    cfg["ws_base_dir"], 
    cfg["dbfs_base_export_dir"], 
    cfg.get("local_artifacts_compare_dir", None),
    cfg["cluster"], cfg["model_name"], 
    cfg["run_name_prefix"], 
    profile)
mlflow_client = mlflow.tracking.MlflowClient()

from databricks_cli.dbfs.api import DbfsApi
api_client = utils.get_api_client(profile)
dbfs_api = DbfsApi(api_client)


TestContext = namedtuple(
    "TestContext",
    [ "tester", "dbfs_api" ]
)


@pytest.fixture(scope="session")
def test_context():
    if tester.local_artifacts_compare_dir: # NOTE: for debugging
        utils_test.create_output_dir(tester.local_artifacts_compare_dir)
    else:
        with tempfile.TemporaryDirectory() as tmpdir:
            tester.local_artifacts_compare_dir = tmpdir
    yield TestContext(tester, dbfs_api)
    tester.teardown()
