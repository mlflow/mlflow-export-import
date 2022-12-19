""" 
Downloads a Databricks notebook with optional revision.
"""

import os
import click

from mlflow_export_import.common.click_options import opt_output_dir
from mlflow_export_import.common import utils, io_utils
from mlflow_export_import.common import MlflowExportImportException
from mlflow_export_import.common.http_client import DatabricksHttpClient


def download_notebook(output_dir, notebook_workspace_path, revision_id, notebook_formats, dbx_client):
    notebook_dir = os.path.join(output_dir)
    os.makedirs(notebook_dir, exist_ok=True)
    for format in notebook_formats:
        _download_notebook(notebook_workspace_path, notebook_dir, format, format.lower(), revision_id, dbx_client)


def _download_notebook(notebook_workspace_path, output_dir, format, extension, revision_id, dbx_client):
    params = { 
        "path": notebook_workspace_path, 
        "direct_download": True,
        "format": format
    }
    if revision_id:
        params["revision_timestamp"] = revision_id # NOTE: not documented publicly
    notebook_name = os.path.basename(notebook_workspace_path)
    try:
        rsp = dbx_client._get("workspace/export", params)
        notebook_path = os.path.join(output_dir, f"{notebook_name}.{extension}")
        io_utils.write_file(notebook_path, rsp.content)
    except MlflowExportImportException as e:
        print(f"WARNING: Cannot download notebook '{notebook_workspace_path}'. {e}")


@click.command()
@opt_output_dir
@click.option("--notebook",
    help="Notebook path.",
    type=str,
    required=True
)
@click.option("--revision",
    help="Notebook revision. If not specified will download the latest revision.",
    type=str,
    required=False
)
@click.option("--notebook-formats",
    help="Databricks notebook formats. Values are SOURCE, HTML, JUPYTER or DBC (comma seperated).",
    type=str,
    default="SOURCE",
    show_default=True
)
def main(output_dir, notebook, revision, notebook_formats):
    print("Options:")
    for k,v in locals().items():
        print(f"  {k}: {v}")
    dbx_client = DatabricksHttpClient()
    notebook_formats = utils.string_to_list(notebook_formats)
    download_notebook(output_dir, notebook, revision, notebook_formats, dbx_client)


if __name__ == "__main__":
    main()
