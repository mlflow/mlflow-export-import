import mlflow
import json
from mlflow_export_import.common import  utils
from mlflow_export_import.common.iterators import SearchRegisteredModelsIterator, SearchModelVersionsIterator

def search_model_versions(client, filter):
    if utils.calling_databricks():
        print(">> SEARCH: CALLING DATABRICKS")
        models = list(SearchRegisteredModelsIterator(client, filter=filter))
        print(f">> SEARCH: Found {len(models)} registered models")
        versions = []
        for model in models:
            try:
                _versions = list(SearchModelVersionsIterator(client, filter=f"name='{model.name}'"))
                versions += _versions
            except Exception as e:
                print(f"ERROR: registered model '{model.name}': {e}")
        return versions
    else:
        print(">> SEARCH: NOT CALLING DATABRICKS")
        return list(SearchModelVersionsIterator(client, filter=filter))


def to_json_signature(signature):
    def _to_json(lst):
        return json.loads(lst) if lst else lst
    return { k:_to_json(v) for k,v in signature.items()}
