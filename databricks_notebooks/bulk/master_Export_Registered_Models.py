# Databricks notebook source
import requests
import json

# COMMAND ----------

dbutils.widgets.removeAll()

# COMMAND ----------

dbutils.widgets.text("01. model_file_name", "") 
model_file_name = dbutils.widgets.get("01. model_file_name")

dbutils.widgets.text("02. Output directory", "/dbfs/mnt/") 
output_dir = dbutils.widgets.get("02. Output directory")
output_dir = output_dir.replace("dbfs:","/dbfs")

dbutils.widgets.multiselect("03. Stages", "Production", ["Production","Staging","Archived","None"])
stages = dbutils.widgets.get("03. Stages")

dbutils.widgets.dropdown("04. Export latest versions","no",["yes","no"])
export_latest_versions = dbutils.widgets.get("04. Export latest versions") == "yes"

dbutils.widgets.dropdown("05. Export permissions","no",["yes","no"])
export_permissions = dbutils.widgets.get("05. Export permissions") == "yes"

dbutils.widgets.dropdown("06. Export deleted runs","no",["yes","no"])
export_deleted_runs = dbutils.widgets.get("06. Export deleted runs") == "yes"

dbutils.widgets.text("07. num_tasks", "1") 
num_tasks = dbutils.widgets.get("07. num_tasks")


import os
os.environ["OUTPUT_DIR"] = output_dir

print("model_file_name:", model_file_name)
print("output_dir:", output_dir)
print("stages:", stages)
print("export_latest_versions:", export_latest_versions)
print("export_permissions:", export_permissions)
print("export_deleted_runs:", export_deleted_runs)
print("num_tasks:", num_tasks)

# COMMAND ----------

if not output_dir:
    raise ValueError("output_dir cannot be empty")
if not output_dir.startswith("/dbfs/mnt"):
    raise ValueError("output_dir must start with /dbfs/mnt")
if not num_tasks:
    raise ValueError("num_tasks cannot be empty")
if not num_tasks.isdigit():
    raise ValueError("num_tasks must be a number")

# COMMAND ----------

if model_file_name:
    if not model_file_name.endswith(".txt"):
        raise ValueError("model_file_name must end with .txt if not empty")
    if not model_file_name.startswith("/dbfs"):
        raise ValueError("model_file_name must start with /dbfs if not empty")
else:
    model_file_name = "all"

model_file_name

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
            "description": f"Bir Task for param1 = {i}",
            "new_cluster": {
                "spark_version": "15.4.x-cpu-ml-scala2.12",
                "node_type_id": worker_node_type,
                "driver_node_type_id": driver_node_type,
                "num_workers": 1,
                "data_security_mode": "SINGLE_USER",
                "runtime_engine": "STANDARD"
            },
            "notebook_task": {
                "notebook_path": "/Workspace/Users/birbal.das@databricks.com/AA_sephora/birnew-mlflow-export-import/databricks_notebooks/bulk/Export_Registered_Models",
                "base_parameters": {
                        "model_file_name" : model_file_name,
                        "output_dir" : output_dir,
                        "stages" : stages,
                        "export_latest_versions" : export_latest_versions,
                        "export_permissions" : export_permissions,
                        "export_deleted_runs" : export_deleted_runs,
                        "task_index": i,
                        "num_tasks" : num_tasks,
                        "run_timestamp": "{{job.start_time.iso_date}}-ExportModels-jobid-{{job.id}}",
                        "jobrunid": "jobrunid-{{job.run_id}}"
                }
            }
        }
        tasks.append(task)

    job_json = {
        "name": "Export_Registered_Models_job",
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

# COMMAND ----------


