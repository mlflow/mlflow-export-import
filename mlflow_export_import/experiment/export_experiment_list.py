""" 
Exports a list of experiments to a directory.
"""

import os
import time
import json
import mlflow
import click
from mlflow_export_import.common import mlflow_utils
from mlflow_export_import import utils, click_doc
from mlflow_export_import.experiment.export_experiment import ExperimentExporter

def export_experiment_list(experiments, output_dir, export_metadata_tags, notebook_formats, export_notebook_revision):
    """
    :param: experiments: Can be either:
      - List of experiment names 
      - List of experiment IDs
      - Dictionary with experiment ID key and list of run IDs 
      - String with comma-delimited experiment names of IDs.
    """
    start_time = time.time()
    client = mlflow.tracking.MlflowClient()

    export_all_runs = not isinstance(experiments,dict) 
    if export_all_runs:
        experiments = utils.get_experiments(experiments)
        table_data = experiments
        columns = ["Experiment ID"]
    else:
        experiments_dct = experiments
        experiments = experiments.keys()
        experiments = utils.get_experiments(experiments)
        table_data = [ [exp_id,len(runs)] for exp_id,runs in experiments_dct.items() ]
        num_runs = sum(x[1] for x in table_data)
        table_data.append(["Total",num_runs])
        columns = ["Experiment ID", "# Runs"]
    utils.show_table("Experiments",table_data,columns)

    exporter = ExperimentExporter(client, export_metadata_tags, utils.string_to_list(notebook_formats), export_notebook_revision)
    export_results = []
    ok_runs = 0
    failed_runs = 0
    print("")
    for exp_id_or_name in experiments:
        exp = mlflow_utils.get_experiment(client, exp_id_or_name)
        out_dir = os.path.join(output_dir, exp.experiment_id)
        run_ids = None
        if not export_all_runs:
            run_ids = experiments_dct.get(exp.experiment_id)
        try:
            _ok_runs, _failed_runs = exporter.export_experiment(exp.experiment_id, out_dir, run_ids)
            ok_runs += _ok_runs
            failed_runs += _failed_runs
            export_results.append( { "id" : exp.experiment_id, "name": exp.name, "ok_runs": _ok_runs, "failed_runs": _failed_runs })
        except Exception:
            import traceback
            traceback.print_exc()
        print("")
    total_runs = ok_runs + failed_runs
    duration = round(time.time() - start_time, 1)

    dct = { 
        "info": {
            "mlflow_version": mlflow.__version__,
            "mlflow_tracking_uri": mlflow.get_tracking_uri(),
            "export_time": utils.get_now_nice(),
            "duration": duration,
            "experiments": len(experiments),
            "total_runs": total_runs,
            "ok_runs": ok_runs,
            "failed_runs": failed_runs
        },
        "experiments": export_results 
    }
    with open(os.path.join(output_dir, "manifest.json"), "w") as f:
        f.write(json.dumps(dct,indent=2)+"\n")

    print(f"{len(experiments)} experiments exported")
    print(f"{ok_runs}/{total_runs} runs succesfully exported")
    if failed_runs > 0:
        print(f"{failed_runs}/{total_runs} runs failed")
    print(f"Experiment export duration: {duration} seonds")

@click.command()
@click.option("--experiments", help="Experiment names or IDs (comma delimited). 'all' will export all experiments. ", required=True, type=str)
@click.option("--output-dir", help="Output directory.", required=True)
@click.option("--export-metadata-tags", help=click_doc.export_metadata_tags, type=bool, default=False, show_default=True)
@click.option("--notebook-formats", help=click_doc.notebook_formats, default="", show_default=True)
@click.option("--export-notebook-revision", help=click_doc.export_notebook_revision, type=bool, default=False, show_default=True)

def main(experiments, output_dir, export_metadata_tags, notebook_formats, export_notebook_revision): # pragma: no cover
    print("Options:")
    for k,v in locals().items():
        print(f"  {k}: {v}")
    export_experiment_list(experiments, output_dir, export_metadata_tags, notebook_formats, export_notebook_revision)

if __name__ == "__main__":
    main()
