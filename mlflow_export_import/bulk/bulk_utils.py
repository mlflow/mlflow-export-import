
import mlflow
from mlflow_export_import.common import MlflowExportImportException

client = mlflow.tracking.MlflowClient()

def get_experiment_ids(experiment_ids):
    """
    Return a list experiment IDS
    """
    if isinstance(experiment_ids,str):
        if experiment_ids == "all":
            return [ exp.experiment_id for exp in client.list_experiments() ]
        elif experiment_ids.endswith("*"):
            exp_prefix = experiment_ids[:-1]
            return [ exp.experiment_id for exp in client.list_experiments() if exp.name.startswith(exp_prefix) ] # Wish there was an experiment search method for efficiency
        else:
            return experiment_ids.split(",")
    elif isinstance(experiment_ids,list):
        return experiment_ids
    else:
        raise MlflowExportImportException(f"Argument to get_experiment_ids() is of type '{type(experiment_ids)}. Must must be a string or list")
