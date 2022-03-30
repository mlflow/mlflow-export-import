import mlflow
from mlflow_export_import.common.iterators import ListRegisteredModelsIterator
from mlflow_export_import.common.iterators import ListExperimentsIterator

client = mlflow.tracking.MlflowClient()

def get_experiment_ids(experiment_ids):
    """
    Return a list experiment IDS
    """
    if isinstance(experiment_ids,str):
        if experiment_ids == "all":
            return [ exp.experiment_id for exp in ListExperimentsIterator(client) ]
        elif experiment_ids.endswith("*"):
            exp_prefix = experiment_ids[:-1]
            return [ exp.experiment_id for exp in ListExperimentsIterator(client) if exp.name.startswith(exp_prefix) ] # Wish there was an experiment search method for efficiency
        else:
            return experiment_ids.split(",")
    elif isinstance(experiment_ids,list):
        return experiment_ids
    else:
        return experiment_ids
        #raise MlflowExportImportException(f"Argument to get_experiment_ids() is of type '{type(experiment_ids)}. Must must be a string or list")

def get_model_names(model_names):
    if isinstance(model_names,str):
        if model_names == "all":
            model_names = [ model.name for model in ListRegisteredModelsIterator(client) ]
        elif model_names.endswith("*"):
            model_prefix = model_names[:-1]
            model_names = [ model.name for model in ListRegisteredModelsIterator(client) if model.name.startswith(model_prefix) ] # TODO: change to search_registered_models
        else:
            model_names = model_names.split(",")
    elif isinstance(model_names,list):
        return model_names
    else:
        return model_names
    return model_names
