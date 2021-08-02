""" 
Exports a run to a directory of zip file.
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
    def __init__(self, client=None, export_metadata_tags=False, notebook_formats=["SOURCE"], filesystem=None):
        self.client = client or mlflow.tracking.MlflowClient()
        self.dbx_client = DatabricksHttpClient()
        print("Databricks REST client:",self.dbx_client)
        self.fs = filesystem or _filesystem.get_filesystem()
        print("Filesystem:",type(self.fs).__name__)
        self.export_metadata_tags = export_metadata_tags
        self.notebook_formats = notebook_formats

    def export_run(self, run_id, output):
        run = self.client.get_run(run_id)
        if output.endswith(".zip"):
            return self.export_run_to_zip(run, output)
        else:
            self.fs.mkdirs(output)
            return self.export_run_to_dir(run, output)

    def export_run_to_zip(self, run, zip_file):
        temp_dir = tempfile.mkdtemp()
        try:
            self.export_run_to_dir(run, temp_dir)
            utils.zip_directory(zip_file, temp_dir)
        finally:
            shutil.rmtree(temp_dir)
            #fs.rm(temp_dir,True) # TODO

    def export_run_to_dir(self, run, run_dir):
        tags =  utils.create_tags_for_metadata(self.client, run, self.export_metadata_tags)
        dct = { "info": utils.strip_underscores(run.info) , 
                "params": run.data.params,
                "metrics": run.data.metrics,
                "tags": tags,
              }
        path = os.path.join(run_dir,"run.json")
        utils.write_json_file(self.fs, path, dct)

        # copy artifacts
        dst_path = os.path.join(run_dir,"artifacts")
        try:
            artifacts = self.client.list_artifacts(run.info.run_id)
            if len(artifacts) > 0: # Because of https://github.com/mlflow/mlflow/issues/2839
                self.fs.mkdirs(dst_path)
                self.client.download_artifacts(run.info.run_id,"", dst_path=mk_local_path(dst_path))
            notebook = tags.get("mlflow.databricks.notebookPath", None)
            if notebook is not None:
                self.export_notebook(run_dir, notebook)
            return True
        except Exception as e:
            print("ERROR: run_id:",run.info.run_id,"Exception:",e)
            traceback.print_exc()
            return False

    def export_notebook(self, run_dir, notebook):
        for format in self.notebook_formats:
            self.export_notebook_format(run_dir, notebook, format, format.lower())

    def export_notebook_format(self, run_dir, notebook, format, extension):
        resource = f"workspace/export?path={notebook}&direct_download=true&format={format}"
        try:
            rsp = self.dbx_client._get(resource)
            nb_name = "notebook."+extension
            nb_path = os.path.join(run_dir,nb_name)
            utils.write_file(nb_path, rsp.content)
            #self.fs.write(nb_path, rsp.content) # Bombs for DBC because dbutils.fs.put only writes strings!
        except MlflowExportImportException as e:
            print(f"WARNING: Cannot save notebook '{notebook}'. {e}")

@click.command()
@click.option("--run-id", help="Run ID.", required=True, type=str)
@click.option("--output", help="Output directory or zip file.", required=True)
@click.option("--export-metadata-tags", help=click_doc.export_metadata_tags, type=bool, default=False, show_default=True)
@click.option("--notebook-formats", help=click_doc.notebook_formats, default="SOURCE", show_default=True)

def main(run_id, output, export_metadata_tags, notebook_formats): # pragma: no cover
    print("Options:")
    for k,v in locals().items():
        print(f"  {k}: {v}")
    exporter = RunExporter(None, export_metadata_tags, utils.string_to_list(notebook_formats))
    exporter.export_run(run_id, output)

if __name__ == "__main__":
    main()
