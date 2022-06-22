from collections import namedtuple
import pytest
import mlflow
from databricks_tester import DatabricksTester
import utils

cfg = utils.read_config_file()
dst_base_dir = cfg["dst_base_dir"]
profile = cfg.get("profile",None)
tester = DatabricksTester(cfg["ws_base_dir"], cfg["dst_base_dir"], cfg["cluster_id"], cfg["model_name"], cfg["run_name_prefix"], profile)
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
    tester.run_job(tester.run_training_job, "Training run")
    yield TestContext(tester, dbfs_api)
