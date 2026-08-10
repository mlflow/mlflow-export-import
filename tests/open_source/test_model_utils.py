from types import SimpleNamespace
from unittest import mock
from mlflow_export_import.common.model_utils import list_model_versions


def test_list_model_versions_fetches_full_version_for_oss():
    """
    Regression test for issue #240.
    search_model_versions omits tags on PostgreSQL backends. list_model_versions
    must call get_model_version per version so tags are present in exported metadata.
    """
    mock_client = mock.Mock()
    full_version = SimpleNamespace(tags={"env": "prod"})
    mock_client.get_model_version.return_value = full_version

    with mock.patch(
        "mlflow_export_import.common.model_utils.SearchModelVersionsIterator",
        return_value=iter([SimpleNamespace(name="m", version="1")]),
    ):
        result = list_model_versions(mock_client, "m")

    assert result == [full_version]
