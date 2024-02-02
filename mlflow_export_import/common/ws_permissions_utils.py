from mlflow_export_import.common import MlflowExportImportException
from mlflow_export_import.common import utils
from mlflow_export_import.client.client_utils import create_dbx_client

_logger = utils.getLogger(__name__)


# == Export permissions

def get_experiment_permissions(dbx_client, experiment_id):
    return _get_permissions(dbx_client, "experiments", experiment_id)


def get_model_permissions_by_id(dbx_client, model_id):
    return _get_permissions(dbx_client, "registered-models", model_id)


def get_model_permissions_by_name(mlflow_client, model_name):
    dbx_client = create_dbx_client(mlflow_client)
    _model = dbx_client.get("mlflow/databricks/registered-models/get", { "name": model_name })
    model_id = _model["registered_model_databricks"]["id"]
    return _get_permissions(dbx_client, "registered-models", model_id)


def _get_permissions(dbx_client, object_type, id):
    perm_levels = _call_get(dbx_client, f"permissions/{object_type}/{id}/permissionLevels")
    perms = _call_get(dbx_client, f"permissions/{object_type}/{id}")
    return { **perm_levels, **{ "permissions": perms } }


def _call_get(dbx_client, resource):
    try:
        return dbx_client.get(resource)
    except MlflowExportImportException as e:
        _logger.error(e.kwargs)
        return {}


# == Import permissions

def update_permissions(dbx_client, perms_in_get_format, object_type, object_name, object_id):
    """
    :param perms_in_get_format: Dict of permissions in GET format
    :param object_type: 'experiment' or 'registered_model'
    :param object_name: name of object
    :param object_id: experiment or registered_model ID
    """
    perms_in_get_format = perms_in_get_format.get("permissions")
    if not perms_in_get_format:
        _logger.warning(f"No permissions for {object_type} '{object_name}'")
        return
    acl_get = perms_in_get_format.get("access_control_list", [])
    resource = f"permissions/{object_type}s/{object_id}"

    acl_put = map_acl(acl_get)
    _logger.info(f"Updating {len(acl_put)} permissions for {object_type} '{object_name}'. Resource: {resource}")

    # We loop for each permission so as not to not cancel the entire update due to an unknown user/group error
    for elt in acl_put:
        acl = { "access_control_list": [elt] }
        _logger.info(f"Updating permissions for {object_type} '{object_name}'. ACL: {acl}")
        try:
            _logger.info(f"Updating permissions for {elt} '{elt}'")
            dbx_client.patch(resource, data=acl)
            _logger.info(f"Updated permissions for {object_type} '{object_name}'")
        except MlflowExportImportException as e:
            _logger.error(f"Error for permissions '{acl}' for {object_type} '{object_name}': {e}")


def map_acl(acl_get_format):
    """
    Maps an ACL list from GET to PUT/PATCH format
    """
    acl_put_format = [ _map_acl_element(elt) for elt in acl_get_format ]
    return [elt for sublist in acl_put_format for elt in sublist]


def _map_acl_element(elt_get_format):
    """
    Maps an ACL element from GET to PUT/PATCH format
    """
    if "group_name" in elt_get_format:
        obj_name = "group_name"
    elif "service_principal_name" in elt_get_format:
        obj_name = "service_principal_name"
    else:
        obj_name = "user_name"
    name = elt_get_format[obj_name]
    return [ {
          obj_name: name,
          "permission_level": perm["permission_level"]
        }
        for perm in elt_get_format["all_permissions"]
    ]
