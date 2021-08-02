""" 
Exports an experiment to a directory.
"""

import os
import mlflow
import shutil
import tempfile
import click

from mlflow_export_import.common import filesystem as _filesystem
from mlflow_export_import.common import mlflow_utils
from mlflow_export_import.common.search_runs_iterator import SearchRunsIterator
from mlflow_export_import.run.export_run import RunExporter
from mlflow_export_import import utils, click_doc

client = mlflow.tracking.MlflowClient()

class ExperimentExporter():
    def __init__(self, client=None, export_metadata_tags=False, notebook_formats=["SOURCE"], filesystem=None):
        self.client = client or mlflow.tracking.MlflowClient()
        self.fs = filesystem or _filesystem.get_filesystem()
        print("Filesystem:",type(self.fs).__name__)
        self.run_exporter = RunExporter(self.client, export_metadata_tags, notebook_formats, self.fs)

    def export_experiment(self, exp_id_or_name, output):
        exp = mlflow_utils.get_experiment(self.client, exp_id_or_name)
        exp_id = exp.experiment_id
        print(f"Exporting experiment '{exp.name}' (ID {exp.experiment_id}) to '{output}'")
        if output.endswith(".zip"):
            self.export_experiment_to_zip(exp_id, output)
        else:
            self.fs.mkdirs(output)
            self.export_experiment_to_dir(exp_id, output)

    def export_experiment_to_dir(self, exp_id, exp_dir):
        exp = self.client.get_experiment(exp_id)
        dct = {"experiment": utils.strip_underscores(exp)}
        run_ids = []
        failed_run_ids = []
        j = 0
        for j,run in enumerate(SearchRunsIterator(self.client, exp_id)):
            run_dir = os.path.join(exp_dir, run.info.run_id)
            print(f"Exporting run {j+1}: {run.info.run_id}")
            res = self.run_exporter.export_run(run.info.run_id, run_dir)
            if res:
                run_ids.append(run.info.run_id)
            else:
                failed_run_ids.append(run.info.run_id)
        dct["export_info"] = { "export_time": utils.get_now_nice(), "num_runs": (j) }
        dct["run_ids"] = run_ids
        dct["failed_run_ids"] = failed_run_ids
        path = os.path.join(exp_dir,"manifest.json")
        utils.write_json_file(self.fs, path, dct)
        if len(failed_run_ids) == 0:
            print(f"All {len(run_ids)} runs succesfully exported")
        else:
            print(f"{len(run_ids)}/{len(infos)} runs succesfully exported")
            print(f"{len(failed_run_ids)}/{len(infos)} runs failed")

    def export_experiment_to_zip(self, exp_id, zip_file):
        temp_dir = tempfile.mkdtemp()
        try:
            self.export_experiment_to_dir(exp_id, temp_dir)
            utils.zip_directory(zip_file, temp_dir)
        finally:
            shutil.rmtree(temp_dir)

@click.command()
@click.option("--experiment", help="Experiment name or ID.", required=True, type=str)
@click.option("--output-dir", help="Output directory.", required=True)
@click.option("--export-metadata-tags", help=click_doc.export_metadata_tags, type=bool, default=False, show_default=True)
@click.option("--notebook-formats", help=click_doc.notebook_formats, default="SOURCE", show_default=True)

def main(experiment, output_dir, export_metadata_tags, notebook_formats): # pragma: no cover
    print("Options:")
    for k,v in locals().items():
        print(f"  {k}: {v}")
    exporter = ExperimentExporter(None, export_metadata_tags, utils.string_to_list(notebook_formats))
    exporter.export_experiment(experiment, output_dir)

if __name__ == "__main__":
    main()
