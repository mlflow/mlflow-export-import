import mlflow
from mlflow_export_import.bulk import bulk_utils

def get_experiments_runs_of_models(client, model_names, show_experiments=False, show_runs=False):
    """ Get experiments and runs to to export. """
    model_names = bulk_utils.get_model_names(client, model_names)
    print("Models:")
    for model_name in model_names:
        print(f"  {model_name}")
    exps_and_runs = {}
    for model_name in model_names:
        versions = client.search_model_versions(f"name='{model_name}'")
        for vr in versions:
            try:
                run = client.get_run(vr.run_id)
                exps_and_runs.setdefault(run.info.experiment_id,[]).append(run.info.run_id)
            except mlflow.exceptions.RestException:
                print(f"WARNING: run {vr.run_id} of version {vr.version} of model '{model_name}' does not exist")
    if show_experiments:
        show_experiments_runs_of_models(exps_and_runs, show_runs)
    return exps_and_runs

def show_experiments_runs_of_models(exps_and_runs, show_runs=False):
    print("Experiments for models:")
    for k,v in exps_and_runs.items():
        print("  Experiment:",k)
        for x in v:
            if show_runs: print("    ",x)
