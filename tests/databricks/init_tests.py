from collections import namedtuple
import pytest
import tempfile

from mlflow_export_import.client import databricks_utils

from tests import utils_test
from tests.databricks.databricks_tester import DatabricksTester

cfg = utils_test.read_config_file()


_tester = DatabricksTester(
    ws_base_dir = cfg["ws_base_dir"], 
    dbfs_base_export_dir = cfg["dbfs_base_export_dir"], 
    local_artifacts_compare_dir = cfg.get("local_artifacts_compare_dir", None),
    cluster_spec = cfg["cluster"], 
    model_name = cfg["model_name"], 
    run_name_prefix = cfg["run_name_prefix"]
)


from databricks_cli.dbfs.api import DbfsApi
_dbfs_api = DbfsApi(databricks_utils.get_api_client())


TestContext = namedtuple(
    "TestContext",
    [ "tester", "dbfs_api" ]
)


@pytest.fixture(scope="session")
def test_context():
    if _tester.local_artifacts_compare_dir: # NOTE: for debugging
        utils_test.create_output_dir(_tester.local_artifacts_compare_dir)
    else:
        with tempfile.TemporaryDirectory() as tmpdir:
            _tester.local_artifacts_compare_dir = tmpdir
    yield TestContext(_tester, _dbfs_api)
    _tester.teardown()
