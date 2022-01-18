
import mlflow

client = mlflow.tracking.MlflowClient()

def get_experiments_runs_of_models(models, show_experiments=False, show_runs=False):
    """ Get experiments and runs to to export. """

    if models == "all":
        models = [ model.name for model in client.list_registered_models() ]
    elif models.endswith("*"):
        model_prefix = models[:-1]
        models = [ model.name for model in client.list_registered_models() if model.name.startswith(model_prefix) ]
    else:
        models = models.split(",")
    print("Models:")
    for model in models:
        print(f"  {model}")
    exps_and_runs = {}
    for model_name in models:
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
