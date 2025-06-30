# Databricks notebook source
import requests
import json
import os
from databricks.sdk import WorkspaceClient

# COMMAND ----------

dbutils.widgets.text("1. Input directory", "") 
input_dir = dbutils.widgets.get("1. Input directory")
input_dir = input_dir.replace("dbfs:","/dbfs")

dbutils.widgets.dropdown("2. Target model registry","unity_catalog",["unity_catalog","workspace_registry"])
target_model_registry = dbutils.widgets.get("2. Target model registry")

dbutils.widgets.text("3. Target catalog for model", "") 
target_model_catalog = dbutils.widgets.get("3. Target catalog for model")

dbutils.widgets.text("4. Target schema for model", "") 
target_model_schema = dbutils.widgets.get("4. Target schema for model")

dbutils.widgets.dropdown("5. Delete model","no",["yes","no"])
delete_model = dbutils.widgets.get("5. Delete model") == "yes"

dbutils.widgets.text("6. Model rename file","")
val = dbutils.widgets.get("6. Model rename file") 
model_rename_file = val or None 

dbutils.widgets.text("7. Experiment rename file","")
val = dbutils.widgets.get("7. Experiment rename file") 
experiment_rename_file = val or None 

dbutils.widgets.dropdown("8. Import permissions","no",["yes","no"])
import_permissions = dbutils.widgets.get("8. Import permissions") == "yes"

dbutils.widgets.text("9. num_tasks", "") 
num_tasks = dbutils.widgets.get("9. num_tasks")

print("input_dir:", input_dir)
print("target_model_registry:", target_model_registry)
print("target_model_catalog:", target_model_catalog)
print("target_model_schema:", target_model_schema)
print("delete_model:", delete_model)
print("model_rename_file:", model_rename_file)
print("experiment_rename_file:", experiment_rename_file)
print("import_permissions:", import_permissions)
print("num_tasks:", num_tasks)

# COMMAND ----------

if not input_dir:
    raise ValueError("input_dir cannot be empty")
if not input_dir.startswith("/dbfs/mnt"):
    raise ValueError("input_dir must start with /dbfs/mnt")
if not num_tasks:
    raise ValueError("num_tasks cannot be empty")
if not num_tasks.isdigit():
    raise ValueError("num_tasks must be a number")

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

DATABRICKS_INSTANCE=dbutils.notebook.entry_point.getDbutils().notebook().getContext().tags().get('browserHostName').getOrElse(None)
DATABRICKS_INSTANCE = f"https://{DATABRICKS_INSTANCE}"
DATABRICKS_TOKEN = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().getOrElse(None)

driver_node_type = "Standard_D4ds_v5"
worker_node_type = "Standard_D4ds_v5"

def create_multi_task_job_json():
    tasks = []
    for i in range(1, int(num_tasks)+1):
        task = {
            "task_key": f"task_{i}",
            "description": f"Import task for task_index = {i}",
            "new_cluster": {
                "spark_version": "15.4.x-cpu-ml-scala2.12",
                "node_type_id": worker_node_type,
                "driver_node_type_id": driver_node_type,
                "num_workers": 1,
                "data_security_mode": "SINGLE_USER",
                "runtime_engine": "STANDARD"
            },
            "notebook_task": {
                "notebook_path": "/Workspace/Users/birbal.das@databricks.com/test_final/bir-mlflow-export-import/databricks_notebooks/bulk/Import_Registered_Models",
                "base_parameters": {
                    "input_dir": os.path.join(input_dir,str(i)),
                    "target_model_registry": target_model_registry,
                    "target_model_catalog": target_model_catalog,
                    "target_model_schema": target_model_schema,
                    "delete_model": delete_model,
                    "model_rename_file": model_rename_file,
                    "experiment_rename_file": experiment_rename_file,
                    "import_permissions": import_permissions,
                    "task_index": str(i)
                }
            }
        }
        tasks.append(task)

    job_json = {
        "name": "Import_Registered_Models_job",
        "tasks": tasks,
        "format": "MULTI_TASK"
    }

    return job_json

def submit_databricks_job():
    job_payload = create_multi_task_job_json()

    headers = {
        "Authorization": f"Bearer {DATABRICKS_TOKEN}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        f"{DATABRICKS_INSTANCE}/api/2.2/jobs/create",
        headers=headers,
        data=json.dumps(job_payload)
    )

    if response.status_code == 200:
        print("Job submitted successfully.")
        print("Response:", response.json())
    else:
        print("Error submitting job:", response.status_code, response.text)



# COMMAND ----------

submit_databricks_job()
