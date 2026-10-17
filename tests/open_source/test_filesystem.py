"""
Tests for common/filesystem.py that do not require a Databricks workspace.
"""

from mlflow_export_import.common import filesystem as fs


def test_mk_local_path():
    assert fs.mk_local_path("dbfs:/tmp/foo") == "/dbfs/tmp/foo"
    assert fs.mk_local_path("/tmp/foo") == "/tmp/foo"


def test_exists_existing_file(tmp_path):
    path = tmp_path / "run.json"
    path.write_text("{}", encoding="utf-8")
    assert fs.exists(str(path)) is True


def test_exists_missing_file(tmp_path):
    assert fs.exists(str(tmp_path / "does-not-exist.json")) is False
