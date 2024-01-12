from mlflow_export_import.common import MlflowExportImportException
from mlflow_export_import.common import utils
from mlflow_export_import.client.http_client import HttpClient

_logger = utils.getLogger(__name__)


class UcPermissionsClient:
    def __init__(self, mlflow_client):
        creds = mlflow_client._tracking_client.store.get_host_creds()
        self.client = HttpClient("api/2.1", creds.host, creds.token)

    def get_permissions(self, model_name):
        """
        https://docs.databricks.com/api/workspace/grants/get
        GET /api/2.1/unity-catalog/permissions/{securable_type}/{full_name}
        """
        resource = f"unity-catalog/permissions/function/{model_name}"
        return self.client.get(resource)

    def get_effective_permissions(self, model_name):
        """
        https://docs.databricks.com/api/workspace/grants/geteffective
        GET /api/2.1/unity-catalog/effective-permissions/{securable_type}/{full_name}
        """
        resource = f"unity-catalog/effective-permissions/function/{model_name}"
        return self.client.get(resource)

    def update_permissions(self, model_name, changes):
        """
        https://docs.databricks.com/api/workspace/grants/update
        PATCH /api/2.1/unity-catalog/permissions/{securable_type}/{full_name}
        """
        resource = f"unity-catalog/permissions/function/{model_name}"
        return self.client.patch(resource, changes)


def get_permissions(mlflow_client, model_name):
    """
    Get permissions and effective permissions of a registered model.
    """
    uc_client = UcPermissionsClient(mlflow_client)
    try:
        return {
            "permissions": uc_client.get_permissions(model_name),
            "effective_permissions": uc_client.get_effective_permissions(model_name)
        }
    except MlflowExportImportException as e:
        _logger.error(f"Cannot get permissions for model '{model_name}'. {e.kwargs}")
        return {}


def update_permissions(mlflow_client, model_name, perms):
    uc_client = UcPermissionsClient(mlflow_client)
    try:
        return uc_client.update_permissions(model_name, _mk_update_changes(perms))
    except MlflowExportImportException as e:
        _logger.error(f"Cannot update permissions for model '{model_name}'. {e.kwargs}")
        return {}

def _mk_update_changes(perms):
    effective_perms = perms.get("effective_permissions", {})
    privilege_assignments = effective_perms.get("privilege_assignments", [])
    def _mk_change(assg):
        privileges = [ pr.get("privilege") for pr in assg.get("privileges") ]
        return { "principal" : assg.get("principal"), "add": privileges }
    changes = [ _mk_change(assg) for assg in privilege_assignments ]
    return { "changes": changes }
