""" 
Exports a run to a directory.
"""

import os
import json
import traceback
import click
import mlflow

from mlflow_export_import.common import utils
from mlflow_export_import.common.click_options import opt_run_id, opt_output_dir, opt_notebook_formats
from mlflow_export_import.common import filesystem as _filesystem
from mlflow_export_import.common import io_utils
from mlflow_export_import.common.timestamp_utils import fmt_ts_millis
from mlflow_export_import.common.http_client import DatabricksHttpClient
from mlflow_export_import.notebook.download_notebook import download_notebook

from mlflow.utils.mlflow_tags import MLFLOW_DATABRICKS_NOTEBOOK_PATH
MLFLOW_DATABRICKS_NOTEBOOK_REVISION_ID = "mlflow.databricks.notebookRevisionID" # NOTE: not in mlflow/utils/mlflow_tags.py

print("MLflow Version:", mlflow.__version__)
print("MLflow Tracking URI:", mlflow.get_tracking_uri())

class RunExporter:

    def __init__(self, mlflow_client, notebook_formats=None):
        """
        :param mlflow_client: MLflow client.
        :param notebook_formats: List of notebook formats to export. Values are SOURCE, HTML, JUPYTER or DBC.
        """
        if notebook_formats is None:
            notebook_formats = []
        self.mlflow_client = mlflow_client
        self.dbx_client = DatabricksHttpClient()
        print("Databricks REST client:", self.dbx_client)
        self.notebook_formats = notebook_formats


    def _get_metrics_with_steps(self, run):
        metrics_with_steps = {}
        for metric in run.data.metrics.keys():
            metric_history = self.mlflow_client.get_metric_history(run.info.run_id,metric)
            lst = [utils.strip_underscores(m) for m in metric_history]
            for x in lst:
                del x["key"] 
            metrics_with_steps[metric] = lst
        return metrics_with_steps


    def export_run(self, run_id, output_dir):
        """
        :param run_id: Run ID.
        :param output_dir: Output directory.
        :return: whether export succeeded.
        """
        run = self.mlflow_client.get_run(run_id)
        tags = run.data.tags
        tags = dict(sorted(tags.items()))
        
        info = utils.strip_underscores(run.info)
        info["_start_time"] = fmt_ts_millis(run.info.start_time)
        info["_end_time"] = fmt_ts_millis(run.info.end_time)
        mlflow_attr = {
            "info": info,
            "params": run.data.params,
            "metrics": self._get_metrics_with_steps(run),
            "tags": tags
        }
        io_utils.write_export_file(output_dir, "run.json", __file__, mlflow_attr)
        fs =  _filesystem.get_filesystem(".")

        # copy artifacts
        dst_path = os.path.join(output_dir, "artifacts")
        try:
            artifacts = self.mlflow_client.list_artifacts(run.info.run_id)
            if len(artifacts) > 0: # Because of https://github.com/mlflow/mlflow/issues/2839
                fs.mkdirs(dst_path)
                self.mlflow_client.download_artifacts(run.info.run_id, "", dst_path=_filesystem.mk_local_path(dst_path))
            notebook = tags.get(MLFLOW_DATABRICKS_NOTEBOOK_PATH, None)
            if notebook is not None:
                if len(self.notebook_formats) > 0:
                    self._export_notebook(output_dir, notebook, run, fs)
            elif len(self.notebook_formats) > 0:
                print(f"WARNING: Cannot export notebook for run '{run_id}' since tag '{MLFLOW_DATABRICKS_NOTEBOOK_PATH}' is not set.")
            return True

        except Exception as e:
            print("ERROR: run_id:", run.info.run_id, "Exception:", e)
            traceback.print_exc()
            return False


    def _export_notebook(self, output_dir, notebook, run, fs):
        notebook_dir = os.path.join(output_dir, "artifacts", "notebooks")
        fs.mkdirs(notebook_dir)
        revision_id = run.data.tags.get(MLFLOW_DATABRICKS_NOTEBOOK_REVISION_ID, None)
        if not revision_id:
            print(f"NOTE: Cannot download notebook '{notebook}' for run '{run.info.run_id}' since tag '{MLFLOW_DATABRICKS_NOTEBOOK_REVISION_ID}' does not exist. Notebook is probably a Git Repo notebook")
            return 
        manifest = { 
           MLFLOW_DATABRICKS_NOTEBOOK_PATH: run.data.tags[MLFLOW_DATABRICKS_NOTEBOOK_PATH],
           MLFLOW_DATABRICKS_NOTEBOOK_REVISION_ID: revision_id,
           "formats": self.notebook_formats
        }
        path = os.path.join(notebook_dir, "manifest.json")
        fs.write(path, (json.dumps(manifest, indent=2)+"\n"))
        download_notebook(notebook_dir, notebook, revision_id, self.notebook_formats, self.dbx_client)


@click.command()
@opt_run_id
@opt_output_dir
@opt_notebook_formats
def main(run_id, output_dir, notebook_formats):
    print("Options:")
    for k,v in locals().items():
        print(f"  {k}: {v}")
    client = mlflow.tracking.MlflowClient()
    exporter = RunExporter(
      client,
      notebook_formats=utils.string_to_list(notebook_formats))
    exporter.export_run(run_id, output_dir)


if __name__ == "__main__":
    main()
