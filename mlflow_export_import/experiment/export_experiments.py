""" 
Exports an experiment to a directory.
"""

import os
import json
import mlflow
import shutil
import tempfile
import click

from mlflow_export_import.common import filesystem as _filesystem
from mlflow_export_import.common import mlflow_utils
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
        infos = self.client.list_run_infos(exp_id)
        dct["export_info"] = { "export_time": utils.get_now_nice(), "num_runs": len(infos) }
        run_ids = []
        failed_run_ids = []
        for j,info in enumerate(infos):
            run_dir = os.path.join(exp_dir, info.run_id)
            print(f"Exporting run {j+1}/{len(infos)}: {info.run_id}")
            res = self.run_exporter.export_run(info.run_id, run_dir)
            if res:
                run_ids.append(info.run_id)
            else:
                failed_run_ids.append(info.run_id)
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
@click.option("--experiments", help="Experiment names or IDs (comma delimited). 'all' will export all experiments. ", required=True, type=str)
@click.option("--output-dir", help="Output directory.", required=True)
@click.option("--export-metadata-tags", help=click_doc.export_metadata_tags, type=bool, default=False, show_default=True)
@click.option("--notebook-formats", help=click_doc.notebook_formats, default="SOURCE", show_default=True)

def main(experiments, output_dir, export_metadata_tags, notebook_formats): # pragma: no cover
    print("Options:")
    for k,v in locals().items():
        print(f"  {k}: {v}")

    if experiments == "all":
        experiments = [ exp.experiment_id for exp in client.list_experiments() ]
    else:
        experiments = experiments.split(",")
    print("Experiments:")
    for exp in experiments:
        print(f"  {exp}")

    exporter = ExperimentExporter(client, export_metadata_tags, utils.string_to_list(notebook_formats))
    lst = []
    for exp_id_or_name in experiments:
        exp = mlflow_utils.get_experiment(client, exp_id_or_name)
        exp_output = os.path.join(output_dir, exp.experiment_id)
        lst.append( { "id" : exp.experiment_id, "name": exp.name } )
        exporter.export_experiment(exp.experiment_id, exp_output)

    dct = { 
        "info": {
            "mlflow_version": mlflow.__version__,
            "mlflow_tracking_uri": mlflow.get_tracking_uri(),
            "export_time": utils.get_now_nice()
        },
        "experiments": lst 
    }
    with open(os.path.join(output_dir, "manifest.json"), "w") as f:
        f.write(json.dumps(dct,indent=2)+"\n")

if __name__ == "__main__":
    main()
