"""
Exports models and their versions' backing run along with the experiment that the run belongs to.
"""

import os
import time
import click
from concurrent.futures import ThreadPoolExecutor

import mlflow

from mlflow_export_import.common.click_options import opt_output_dir, opt_notebook_formats, \
    opt_stages, opt_use_threads, opt_export_latest_versions
from mlflow_export_import.common import utils, io_utils
from mlflow_export_import.model.export_model import ModelExporter
from mlflow_export_import.bulk import export_experiments
from mlflow_export_import.bulk.model_utils import get_experiments_runs_of_models
from mlflow_export_import.bulk import bulk_utils


def _export_models(client, 
        model_names, 
        output_dir, 
        notebook_formats, 
        stages, 
        export_run=True, 
        use_threads=False, 
        export_latest_versions=False
    ):
    max_workers = os.cpu_count() or 4 if use_threads else 1
    start_time = time.time()
    model_names = bulk_utils.get_model_names(client, model_names)
    print("Models to export:")
    for model_name in model_names:
        print(f"  {model_name}")

    exporter = ModelExporter(client, 
        notebook_formats=utils.string_to_list(notebook_formats), 
        stages=stages, 
        export_run=export_run,
        export_latest_versions=export_latest_versions
    )
    futures = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for model_name in model_names:
            dir = os.path.join(output_dir, model_name)
            future = executor.submit(exporter.export_model, model_name, dir)
            futures.append(future)
    ok_models = [] ; failed_models = []
    for future in futures:
        result = future.result()
        if result[0]: ok_models.append(result[1])
        else: failed_models.append(result[1])
    duration = round(time.time()-start_time, 1)

    info_attr = {
        "model_names": model_names,
        "stages": stages,
        "export_run": export_run,
        "export_latest_versions": export_latest_versions,
        "notebook_formats": notebook_formats,
        "use_threads": use_threads,
        "output_dir": output_dir,
        "num_total_models": len(model_names),
        "num_ok_models": len(ok_models),
        "num_failed_models": len(failed_models),
        "duration": duration,
        "failed_models": failed_models
    }
    mlflow_attr = {
        "models": ok_models,
    }
    io_utils.write_export_file(output_dir, "models.json", __file__, mlflow_attr, info_attr)

    print(f"{len(model_names)} models exported")
    print(f"Duration for registered models export: {duration} seconds")

    return info_attr


def export_models(client, 
        model_names, 
        output_dir, 
        notebook_formats=None, 
        stages="", 
        export_all_runs=False, 
        use_threads=False, 
        export_latest_versions=False
    ):
    exps_and_runs = get_experiments_runs_of_models(client, model_names)
    exp_ids = exps_and_runs.keys()
    start_time = time.time()
    out_dir = os.path.join(output_dir, "experiments")
    exps_to_export = exp_ids if export_all_runs else exps_and_runs
    res_exps = export_experiments.export_experiments(client, exps_to_export, out_dir, notebook_formats, use_threads)
    res_models =_export_models(client, model_names, os.path.join(output_dir,"models"), notebook_formats, stages,
        export_run=False, use_threads=use_threads, export_latest_versions=export_latest_versions)
    duration = round(time.time()-start_time, 1)
    print(f"Duration for total registered models and versions' runs export: {duration} seconds")

    info_attr = {
        "model_names": model_names,
        "stages": stages,
        "export_all_runs": export_all_runs,
        "export_latest_versions": export_latest_versions,
        "notebook_formats": notebook_formats,
        "use_threads": use_threads,
        "output_dir": output_dir,
        "models": res_models,
        "experiments": res_exps
    }
    io_utils.write_export_file(output_dir, "manifest.json", __file__, {}, info_attr)

    return info_attr


@click.command()
@opt_output_dir
@click.option("--models", 
    help="Registered model names (comma delimited).  \
        For example, 'model1,model2'. 'all' will export all models.",
    type=str,
    required=True
)
@opt_export_latest_versions
@opt_stages
@click.option("--export-all-runs", 
    help="Export all runs of experiment or just runs associated with registered model versions.", 
    type=bool, 
    default=False, 
    show_default=True
)
@opt_notebook_formats
@opt_use_threads
def main(models, output_dir, stages, notebook_formats, export_all_runs, use_threads, export_latest_versions):
    print("Options:")
    for k,v in locals().items():
        print(f"  {k}: {v}")
    client = mlflow.tracking.MlflowClient()
    export_models(client,
        models, 
        output_dir=output_dir, 
        notebook_formats=notebook_formats, 
        stages=stages, 
        export_all_runs=export_all_runs, 
        export_latest_versions=export_latest_versions, 
        use_threads=use_threads)


if __name__ == "__main__":
    main()
