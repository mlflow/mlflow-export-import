# Databricks notebook source
# Common - copy model version

# COMMAND ----------

# MAGIC %pip install git+https:///github.com/mlflow/mlflow-export-import@issue-138-copy-model-version#egg=mlflow-export-import

# COMMAND ----------

import mlflow
print("mlflow.version:", mlflow.__version__)

# COMMAND ----------

from mlflow_export_import.common.dump_utils import obj_to_dict, dict_to_json, dump_obj_as_json

# COMMAND ----------

def assert_widget(value, name):
    if len(value.rstrip())==0: 
        raise Exception(f"ERROR: '{name}' widget is required")

# COMMAND ----------

from mlflow.utils import databricks_utils
mlflow_client = mlflow.MlflowClient()

_host_name = databricks_utils.get_browser_hostname()
print("host_name:", _host_name)

def display_registered_model_version_uri(model_name, version):
    if _host_name:
        if "." in model_name: # is unity catalog model
            model_name = model_name.replace(".","/")
            uri = f"https://{_host_name}/explore/data/models/{model_name}/version/{version}"
        else:
            uri = f"https://{_host_name}/#mlflow/models/{model_name}/versions/{version}"
        displayHTML("""<b>Registered Model Version URI:</b> <a href="{}">{}</a>""".format(uri,uri))

def display_run_uri(run_id):
    if _host_name:
        run = mlflow_client.get_run(run_id)
        uri = f"https://{_host_name}/#mlflow/experiments/{run.info.experiment_id}/runs/{run_id}"
        displayHTML("""<b>Run URI:</b> <a href="{}">{}</a>""".format(uri,uri))

# COMMAND ----------

def copy_model_version(
        src_model_name,
        src_model_version,
        dst_model_name,
        dst_experiment_name, 
        src_run_workspace = "databricks",
        add_copy_system_tags = False,
        verbose = False 
    ):
    from mlflow_export_import.common.model_utils import is_unity_catalog_model 
    from mlflow_export_import.copy.copy_model_version import copy
      
    def mk_registry_uri(model_name):
        return "databricks-uc" if is_unity_catalog_model(model_name) else "databricks"

    src_registry_uri = mk_registry_uri(src_model_name)
    dst_registry_uri = mk_registry_uri(dst_model_name)
    print("src_registry_uri:", src_registry_uri)
    print("dst_registry_uri:", dst_registry_uri)

    return copy(
        src_model_name,
        src_model_version,
        dst_model_name,
        dst_experiment_name, 
        src_tracking_uri = src_run_workspace,
        dst_tracking_uri = "databricks",
        src_registry_uri = src_registry_uri, 
        dst_registry_uri = dst_registry_uri,
        add_copy_system_tags = add_copy_system_tags,
        verbose = verbose 
    )
