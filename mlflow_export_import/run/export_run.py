""" 
Exports a run to a directory.
"""

import os
import shutil
import traceback
import tempfile
import mlflow
import click

from mlflow_export_import.common import filesystem as _filesystem
from mlflow_export_import.common.filesystem import mk_local_path
from mlflow_export_import.common.http_client import DatabricksHttpClient
from mlflow_export_import.common import MlflowExportImportException
from mlflow_export_import import utils, click_doc

print("MLflow Version:", mlflow.version.VERSION)
print("MLflow Tracking URI:", mlflow.get_tracking_uri())

class RunExporter():
    def __init__(self, client=None, export_metadata_tags=False, notebook_formats=[]):
        self.client = client or mlflow.tracking.MlflowClient()
        self.dbx_client = DatabricksHttpClient()
        print("Databricks REST client:",self.dbx_client)
        self.export_metadata_tags = export_metadata_tags
        self.notebook_formats = notebook_formats

    def export_run(self, run_id, output_dir):
        fs = _filesystem.get_filesystem(output_dir)
        #print("Filesystem:",type(fs).__name__)
        run = self.client.get_run(run_id)
        fs.mkdirs(output_dir)
        tags =  utils.create_tags_for_metadata(self.client, run, self.export_metadata_tags)
        dct = { "info": utils.strip_underscores(run.info) , 
                "params": run.data.params,
                "metrics": run.data.metrics,
                "tags": tags,
              }
        path = os.path.join(output_dir,"run.json")
        utils.write_json_file(fs, path, dct)

        # copy artifacts
        dst_path = os.path.join(output_dir,"artifacts")
        try:
            TAG_NOTEBOOK_PATH = "mlflow.databricks.notebookPath"
            artifacts = self.client.list_artifacts(run.info.run_id)
            if len(artifacts) > 0: # Because of https://github.com/mlflow/mlflow/issues/2839
                fs.mkdirs(dst_path)
                self.client.download_artifacts(run.info.run_id,"", dst_path=mk_local_path(dst_path))
            notebook = tags.get(TAG_NOTEBOOK_PATH, None)
            if notebook is not None:
                if len(self.notebook_formats) > 0:
                    self.export_notebook(output_dir, notebook, run.data.tags, fs)
            elif len(self.notebook_formats) > 0:
                print(f"WARNING: Cannot export notebook since tag '{TAG_NOTEBOOK_PATH}' is not set.")
            return True
        except Exception as e:
            print("ERROR: run_id:",run.info.run_id,"Exception:",e)
            traceback.print_exc()
            return False

    def export_notebook(self, output_dir, notebook, tags, fs):
        notebook_dir = os.path.join(output_dir,"artifacts","notebooks")
        fs.mkdirs(notebook_dir)
        for format in self.notebook_formats:
            self.export_notebook_format(notebook_dir, notebook, format, format.lower(), tags)

    def export_notebook_format(self, notebook_dir, notebook, format, extension, tags):
        revision = tags["mlflow.databricks.notebookRevisionID"]
        notebook_name = os.path.basename(tags["mlflow.databricks.notebookPath"])
        resource = f'workspace/export?path={notebook}&direct_download=true&format={format}&revision={{"revision_timestamp":{revision}}}'
        try:
            rsp = self.dbx_client._get(resource)
            notebook_path = os.path.join(notebook_dir, f"{notebook_name}.{extension}")
            utils.write_file(notebook_path, rsp.content)
        except MlflowExportImportException as e:
            print(f"WARNING: Cannot save notebook '{notebook}'. {e}")

@click.command()
@click.option("--run-id", help="Run ID.", required=True, type=str)
@click.option("--output-dir", help="Output directory.", required=True)
@click.option("--export-metadata-tags", help=click_doc.export_metadata_tags, type=bool, default=False, show_default=True)
@click.option("--notebook-formats", help=click_doc.notebook_formats, default="", show_default=True)

def main(run_id, output_dir, export_metadata_tags, notebook_formats): # pragma: no cover
    print("Options:")
    for k,v in locals().items():
        print(f"  {k}: {v}")
    exporter = RunExporter(None, export_metadata_tags, utils.string_to_list(notebook_formats))
    exporter.export_run(run_id, output_dir)

if __name__ == "__main__":
    main()
