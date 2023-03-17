
from mlflow_export_import.client.http_client import DatabricksHttpClient
from mlflow_export_import.common import MlflowExportImportException
#from mlflow_export_import.common import utils

dbx_client = DatabricksHttpClient()

def add_experiment_permissions(experiment_id, dct):
    perm_levels = _call(f"permissions/experiments/{experiment_id}/permissionLevels", "permission_levels")
    perms = _call(f"permissions/experiments/{experiment_id}")
    dct["permissions"] = { **perm_levels, **{ "permissions": perms } }


def add_model_permissions(model):
    model_id = model["id"]
    perm_levels = _call(f"permissions/registered-models/{model_id}/permissionLevels","permission_levels")
    perms = _call(f"permissions/registered-models/{model_id}")
    model["permissions"] = { **perm_levels, **{ "permissions": perms } }


def _call(path, root=None):
    try:
        return dbx_client.get(path)
    except MlflowExportImportException as e:
        from mlflow_export_import.common import mlflow_utils
        #print("ERROR:",e)
        print("ERROR:",e.kwargs)
        mlflow_utils.dump_exception(e)
        error = { "error": e.kwargs }
        if root:
            error = { root: error }
        return error
