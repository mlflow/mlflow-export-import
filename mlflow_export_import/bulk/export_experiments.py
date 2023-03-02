""" 
Exports experiments to a directory.
"""

import os
import time
from concurrent.futures import ThreadPoolExecutor
import click
import mlflow

from mlflow_export_import.common.click_options import opt_experiments, opt_output_dir, \
    opt_notebook_formats, opt_use_threads
from mlflow_export_import.common import utils, io_utils, mlflow_utils
from mlflow_export_import.bulk import bulk_utils
from mlflow_export_import.experiment.export_experiment import ExperimentExporter


def _export_experiment(client, exp_id_or_name, output_dir, exporter, export_results, run_ids):
    exp = mlflow_utils.get_experiment(client, exp_id_or_name)
    exp_output = os.path.join(output_dir, exp.experiment_id)
    ok_runs = -1; failed_runs = -1
    try:
        start_time = time.time()
        ok_runs, failed_runs = exporter.export_experiment(exp.experiment_id, exp_output, run_ids)
        duration = round(time.time() - start_time, 1)
        result = {
            "id" : exp.experiment_id, 
            "name": exp.name, 
            "ok_runs": ok_runs, 
            "failed_runs": failed_runs,
            "duration": duration
        }
        export_results.append(result)
        print(f"Done exporting experiment {result}")
    except Exception:
        import traceback
        traceback.print_exc()
    return ok_runs, failed_runs


def export_experiments(client, experiments, output_dir, notebook_formats=None, use_threads=False):
    """
    :param: experiments: Can be either:
      - List of experiment names 
      - List of experiment IDs
      - Dictionary whose key is an experiment and the value is a list of run IDs 
      - String with comma-delimited experiment names or IDs such as 'sklearn_wine,sklearn_iris' or '1,2'
    """
    start_time = time.time()
    max_workers = os.cpu_count() or 4 if use_threads else 1

    export_all_runs = not isinstance(experiments, dict) 
    experiments = bulk_utils.get_experiment_ids(client, experiments)
    if export_all_runs:
        table_data = experiments
        columns = ["Experiment Name or ID"]
        experiments_dct = {}
    else:
        experiments_dct = experiments # we passed in a dict
        experiments = experiments.keys()
        table_data = [ [exp_id,len(runs)] for exp_id,runs in experiments_dct.items() ]
        num_runs = sum(x[1] for x in table_data)
        table_data.append(["Total",num_runs])
        columns = ["Experiment ID", "# Runs"]
    utils.show_table("Experiments",table_data,columns)
    print("")

    ok_runs = 0
    failed_runs = 0
    export_results = []
    futures = []
    exporter = ExperimentExporter(client, notebook_formats=utils.string_to_list(notebook_formats))
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for exp_id_or_name in experiments:
            run_ids = experiments_dct.get(exp_id_or_name, None)
            future = executor.submit(_export_experiment, client, exp_id_or_name, output_dir, exporter, export_results, run_ids)
            futures.append(future)
    duration = round(time.time() - start_time, 1)
    ok_runs = 0
    failed_runs = 0
    for future in futures:
        result = future.result()
        ok_runs += result[0]
        failed_runs += result[1]
    
    total_runs = ok_runs + failed_runs
    duration = round(time.time() - start_time, 1)

    info_attr = {
      "duration": duration,
      "experiments": len(experiments),
      "total_runs": total_runs,
      "ok_runs": ok_runs,
      "failed_runs": failed_runs
    }
    mlflow_attr = { "experiments": export_results }
    io_utils.write_export_file(output_dir, "experiments.json", __file__, mlflow_attr, info_attr)

    print(f"{len(experiments)} experiments exported")
    print(f"{ok_runs}/{total_runs} runs succesfully exported")
    if failed_runs > 0:
        print(f"{failed_runs}/{total_runs} runs failed")
    print(f"Duration for experiments export: {duration} seconds")

    return info_attr


@click.command()
@opt_experiments
@opt_output_dir
@opt_notebook_formats
@opt_use_threads
def main(experiments, output_dir, notebook_formats, use_threads): 
    print("Options:")
    for k,v in locals().items():
        print(f"  {k}: {v}")
    client = mlflow.tracking.MlflowClient()
    export_experiments(client, 
        experiments=experiments,
        output_dir=output_dir,
        notebook_formats=notebook_formats,
        use_threads=use_threads)


if __name__ == "__main__":
    main()
