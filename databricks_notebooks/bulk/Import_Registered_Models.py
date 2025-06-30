# Databricks notebook source
# MAGIC %md ## Import Registered Models
# MAGIC
# MAGIC Widgets 
# MAGIC * `1. Input directory` - directory of exported models. 
# MAGIC * `2. Delete model` - delete the current contents of model
# MAGIC * `3. Model rename file` - Model rename file.
# MAGIC * `4. Experiment rename file` - Experiment rename file.
# MAGIC * `5. Import permissions`
# MAGIC * `6. Import source tags`
# MAGIC * `7. Use threads` - use multi-threaded import.
# MAGIC
# MAGIC See https://github.com/mlflow/mlflow-export-import/blob/master/README_bulk.md#Import-registered-models

# COMMAND ----------

# MAGIC %run ./Common

# COMMAND ----------

from mlflow_export_import.bulk import config
import time
from datetime import datetime
from databricks.sdk import WorkspaceClient

# COMMAND ----------

dbutils.widgets.text("input_dir", "") 
input_dir = dbutils.widgets.get("input_dir")
input_dir = input_dir.replace("dbfs:","/dbfs")

dbutils.widgets.dropdown("target_model_registry","unity_catalog",["unity_catalog","workspace_registry"])
target_model_registry = dbutils.widgets.get("target_model_registry")

dbutils.widgets.text("target_model_catalog", "") 
target_model_catalog = dbutils.widgets.get("target_model_catalog")

dbutils.widgets.text("target_model_schema", "") 
target_model_schema = dbutils.widgets.get("target_model_schema")

dbutils.widgets.dropdown("delete_model","false",["true","false"])
delete_model = dbutils.widgets.get("delete_model") == "true"

dbutils.widgets.text("model_rename_file","")
val = dbutils.widgets.get("model_rename_file") 
model_rename_file = {} if val in ("null", None, "") else val

dbutils.widgets.text("experiment_rename_file","")
val = dbutils.widgets.get("experiment_rename_file") 
experiment_rename_file = {} if val in ("null", None, "") else val

dbutils.widgets.dropdown("import_permissions","false",["true","false"])
import_permissions = dbutils.widgets.get("import_permissions") == "true"

dbutils.widgets.text("task_index", "") 
task_index = dbutils.widgets.get("task_index")


print("input_dir:", input_dir)
print("target_model_registry:", target_model_registry)
print("target_model_catalog:", target_model_catalog)
print("target_model_schema:", target_model_schema)
print("delete_model:", delete_model)
print("model_rename_file:     ", model_rename_file)
print("experiment_rename_file:", experiment_rename_file)
print("import_permissions:", import_permissions)
print("task_index:", task_index)

# COMMAND ----------

print(f"experiment_rename_file is {experiment_rename_file}")
print(f"experiment_rename_file type is {type(experiment_rename_file)}")

print(f"model_rename_file is {model_rename_file}")
print(f"model_rename_file type is {type(model_rename_file)}")

print(f"delete_model is {delete_model}")
print(f"import_permissions is {import_permissions}")

# COMMAND ----------

if not input_dir:
    raise ValueError("input_dir cannot be empty")
if not input_dir.startswith("/dbfs/mnt"):
    raise ValueError("input_dir must start with /dbfs/mnt")
if not task_index:
    raise ValueError("task_index cannot be empty")
if not task_index.isdigit():
    raise ValueError("task_index must be a number")

# COMMAND ----------

if target_model_registry == "workspace_registry":
    target_model_catalog = None
    target_model_schema = None

# COMMAND ----------

if target_model_registry == "unity_catalog" and (not target_model_catalog or not target_model_schema):
    raise ValueError("target_model_catalog and target_model_schema cannot be blank when target_model_registry is 'unity_catalog'")

# COMMAND ----------

w = WorkspaceClient()
try:
    catalog = w.catalogs.get(name=target_model_catalog)
    print(f"Catalog '{target_model_catalog}' exists.")
except Exception as e:
    raise ValueError(f"Error - {e}")

# COMMAND ----------

try:
    schema = w.schemas.get(full_name=f"{target_model_catalog}.{target_model_schema}")
    print(f"Schema '{target_model_catalog}.{target_model_schema}' exists.")    
except Exception as e:
    raise ValueError(f"Error - {e}")    

# COMMAND ----------

if input_dir.startswith("/Workspace"):
    input_dir=input_dir.replace("/Workspace","file:/Workspace") 

input_dir

# COMMAND ----------

log_path=f"/tmp/Import_Registered_Models_{task_index}.log"
log_path

# COMMAND ----------

config.log_path=log_path
config.target_model_registry=target_model_registry

# COMMAND ----------

from mlflow_export_import.bulk.import_models import import_models

import_models(
    input_dir = input_dir,
    delete_model = delete_model,
    model_renames = model_rename_file,
    experiment_renames = experiment_rename_file,
    import_permissions = import_permissions,
    import_source_tags = False, ## Birbal:: Do not set to True. else it will import junk mlflow tags. Setting to False WILL import all source tags by default.
    use_threads = True,
    target_model_catalog = target_model_catalog, #birbal added
    target_model_schema = target_model_schema   #birbal added
)

# COMMAND ----------

time.sleep(10)

# COMMAND ----------

curr_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

dbfs_log_path = f"{input_dir}/Import_Registered_Models_{task_index}_{curr_timestamp}.log"
if dbfs_log_path.startswith("/Workspace"):
    dbfs_log_path=dbfs_log_path.replace("/Workspace","file:/Workspace") 
dbfs_log_path = dbfs_log_path.replace("/dbfs","dbfs:")
dbfs_log_path

# COMMAND ----------


dbutils.fs.cp(f"file:{log_path}", dbfs_log_path)

# COMMAND ----------

print(dbutils.fs.head(dbfs_log_path))
