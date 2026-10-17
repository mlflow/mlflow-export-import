"""
Tests for run/import_run.py that do not require a Databricks workspace.
"""

import base64
import os

from mlflow_export_import.run.import_run import _upload_databricks_notebook


class MockDbxClient():
    def __init__(self):
        self.calls = []

    def post(self, resource, data=None):
        self.calls.append((resource, data))

    def _post(self, resource, data=None):
        self.calls.append((resource, data))

    def workspace_imports(self):
        return [ data for resource, data in self.calls if resource == "workspace/import" ]


def _mk_src_run_dct(notebook_path="/Users/me@example.com/notebook"):
    return {
        "info": { "run_id": "src_run_id" },
        "tags": { "mlflow.databricks.notebookPath": notebook_path }
    }


def _mk_input_dir(input_dir, content=None):
    notebook_dir = os.path.join(input_dir, "artifacts", "notebooks")
    os.makedirs(notebook_dir, exist_ok=True)
    if content is not None:
        with open(os.path.join(notebook_dir, "notebook.source"), "w", encoding="utf-8") as f:
            f.write(content)


def test_upload_databricks_notebook(tmp_path):
    input_dir = str(tmp_path)
    content = "print('hello')"
    _mk_input_dir(input_dir, content)
    dbx_client = MockDbxClient()

    _upload_databricks_notebook(dbx_client, input_dir, _mk_src_run_dct(), "/Users/me@example.com/dst")

    imports = dbx_client.workspace_imports()
    assert len(imports) == 1
    assert imports[0]["path"] == os.path.join("/Users/me@example.com/dst", "notebook")
    assert base64.b64decode(imports[0]["content"]).decode("utf-8") == content


def test_upload_databricks_notebook_missing_source(tmp_path):
    input_dir = str(tmp_path)
    _mk_input_dir(input_dir)
    dbx_client = MockDbxClient()

    _upload_databricks_notebook(dbx_client, input_dir, _mk_src_run_dct(), "/Users/me@example.com/dst")

    assert dbx_client.workspace_imports() == []
