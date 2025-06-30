from mlflow_export_import.common.iterators import SearchRegisteredModelsIterator
from mlflow_export_import.common.iterators import SearchExperimentsIterator
from mlflow_export_import.common import utils   #birbal added

_logger = utils.getLogger(__name__)     #birbal added

def _get_list(names, func_list, task_index=None, num_tasks=None): #birbal updated
    """
    Returns a list of entities specified by the 'names' filter.
    :param names: Filter of desired list of entities. Can be: "all", comma-delimited string, list of entities or trailing wildcard "*".
    :param func_list: Function that lists the entities primary keys - for experiments it is experiment_id, for registered models it is model name.
    :return: List of entities.
    """
    if isinstance(names, str):
        if names == "all":
            if task_index is None or num_tasks is None:
                return func_list()
            else:
                all_items=func_list()
                _logger.info(f"TOTAL MODEL IN THE WORKSPACE REGISTRY IS {len(all_items)}")
                return get_subset_list(all_items, task_index, num_tasks)


        elif names.endswith("*"):
            prefix = names[:-1]
            return [ x for x in func_list() if x.startswith(prefix) ] 
        else:
            return names.split(",")
    else:
        return names




def get_experiment_ids(mlflow_client, experiment_ids):
    def list_entities():
        return [ exp.experiment_id for exp in SearchExperimentsIterator(mlflow_client) ]
    return _get_list(experiment_ids, list_entities)


# def get_model_names(mlflow_client, model_names):
def get_model_names(mlflow_client, model_names,task_index=None,num_tasks=None): #birbal updated
    def list_entities():
        return [ model.name for model in SearchRegisteredModelsIterator(mlflow_client) ]
    return _get_list(model_names, list_entities, task_index, num_tasks) #birbal updated


def get_subset_list(fulllist, task_index, num_tasks):  
    fulllist.sort()  
    total_items = len(fulllist)
    base_size, remainder = divmod(total_items, num_tasks)

    if task_index <= remainder:        
        start = (base_size + 1) * (task_index - 1)
        end = start + base_size + 1
    else:        
        start = (base_size + 1) * remainder + base_size * (task_index - remainder - 1)
        end = start + base_size

    return fulllist[start:end]

