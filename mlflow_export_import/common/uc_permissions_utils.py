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

    # def update_permissions(self, model_name, changes): #birbal commented out entire func def
    #     """
    #     https://docs.databricks.com/api/workspace/grants/update
    #     PATCH /api/2.1/unity-catalog/permissions/{securable_type}/{full_name}
    #     """
    #     resource = f"unity-catalog/permissions/function/{model_name}"
    #     _logger.info(f"Updating {len(changes.get('changes',[]))} permissions for model '{model_name}'. Resource: {resource}")
    #     return self.client.patch(resource, changes)

    
    def update_permissions(self, object_type, object_name , changes): #birbal modified the above block
        """
        https://docs.databricks.com/api/workspace/grants/update
        PATCH /api/2.1/unity-catalog/permissions/{securable_type}/{full_name}
        """
        resource = f"unity-catalog/permissions/{object_type}/{object_name}"
        _logger.info(f"Updating {len(changes.get('changes',[]))} permissions for {object_type} '{object_name}'. Resource: {resource}")
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



def update_permissions_nonucsrc_uctgt(mlflow_client, model_name, perms): ##birbal added this entire func.

    try:
        _logger.info(f"BEFORE perms is {perms}")
        uc_client = UcPermissionsClient(mlflow_client)
        model_perm_dict, catalog_perm_dict, schema_perm_dict = format_perms(perms)
        _logger.info(f"AFTER model_perm_dict is {model_perm_dict}")
        _logger.info(f"AFTER catalog_perm_dict is {catalog_perm_dict}")
        _logger.info(f"AFTER schema_perm_dict is {schema_perm_dict}")

        catalog, schema, model = model_name.split(".")

        uc_client.update_permissions("catalog", catalog, catalog_perm_dict)
        uc_client.update_permissions("schema", catalog+"."+schema, schema_perm_dict)
        uc_client.update_permissions("function", model_name, model_perm_dict)
    except Exception as e:
        _logger.error(f"error with update_permissions for model '{model_name}'. Error: {e}")


def format_perms(perms):    ##birbal added this entire func.
    model_perm = []
    catalog_perm=[]
    schema_perm=[]

    for acl in perms['permissions']['access_control_list']:
            permission_type = "EXECUTE"
            for perm in acl['all_permissions']:
                if perm.get('permission_level') == 'CAN_MANAGE':
                    permission_type = "MANAGE"
                    break
            if 'user_name' in acl:
              model_perm.append({
                  "add": [permission_type],
                  "principal": acl['user_name']
              })
              catalog_perm.append({
                  "add": ["USE_CATALOG"],
                  "principal": acl['user_name']
              })
              schema_perm.append({
                  "add": ["USE_SCHEMA"],
                  "principal": acl['user_name']
              })              

            if 'group_name' in acl:
              group_name = acl['group_name']
              if group_name == "admins":
                  continue
              model_perm.append({
                  "add": [permission_type],
                  "principal": group_name
              })
              catalog_perm.append({
                  "add": ["USE_CATALOG"],
                  "principal": group_name
              })
              schema_perm.append({
                  "add": ["USE_SCHEMA"],
                  "principal": group_name
              })  

    model_perm_dict = {"changes": model_perm}
    catalog_perm_dict = {"changes": catalog_perm}
    schema_perm_dict = {"changes": schema_perm}
    return model_perm_dict,catalog_perm_dict,schema_perm_dict




def update_permissions(mlflow_client, model_name, perms, unroll_changes=True): 
    uc_client = UcPermissionsClient(mlflow_client)
    changes = _mk_update_changes(perms)
    if unroll_changes: # NOTE: in order to prevent batch update to fail because one individual update failed
        unrolled_changes = _mk_unrolled_changes(changes)
        for _changes in unrolled_changes:
            _update_changes(uc_client, model_name, _changes)
    else:
        _update_changes(uc_client, model_name, changes)

def _update_changes(uc_client, model_name, changes):
    try:
        return uc_client.update_permissions(model_name, changes)
    except MlflowExportImportException as e:
        _logger.error(f"Cannot update permissions for model '{model_name}'. {e.kwargs}")
        return {}

def _mk_update_changes(perms):
    """
    Transform permissions GET response to PATCH request JSON format
    """
    def _mk_change(assg):
        privileges = [ pr.get("privilege") for pr in assg.get("privileges") ]
        return { "principal" : assg.get("principal"), "add": privileges }
    effective_perms = perms.get("effective_permissions", {})
    privilege_assignments = effective_perms.get("privilege_assignments", [])
    changes = [ _mk_change(assg) for assg in privilege_assignments ]
    return { "changes": changes }

def _mk_unrolled_changes(changes):
    return [ { "changes":[ch] } for ch in changes["changes"] ]
