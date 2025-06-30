# Databricks notebook source
import requests
import json
from datetime import datetime

# COMMAND ----------

dbutils.widgets.text("1. Output directory", "") 
output_dir = dbutils.widgets.get("1. Output directory")
output_dir = output_dir.replace("dbfs:","/dbfs")

dbutils.widgets.multiselect("2. Stages", "Production", ["Production","Staging","Archived","None"])
stages = dbutils.widgets.get("2. Stages")

dbutils.widgets.dropdown("3. Export latest versions","no",["yes","no"])
export_latest_versions = dbutils.widgets.get("3. Export latest versions") == "yes"

dbutils.widgets.text("4. Run start date", "") 
run_start_date = dbutils.widgets.get("4. Run start date")

dbutils.widgets.dropdown("5. Export permissions","no",["yes","no"])
export_permissions = dbutils.widgets.get("5. Export permissions") == "yes"

dbutils.widgets.text("11. num_tasks", "") 
num_tasks = dbutils.widgets.get("11. num_tasks")
 
print("output_dir:", output_dir)
print("stages:", stages)
print("export_latest_versions:", export_latest_versions)
print("run_start_date:", run_start_date)
print("export_permissions:", export_permissions)
print("num_tasks:", num_tasks)

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
                "notebook_path": "/Workspace/Users/birbal.das@databricks.com/mlflowimport/bir-mlflow-export-import/databricks_notebooks/bulk/Export_All",
                "base_parameters": {
                    "output_dir": output_dir,
                    "stages": stages,
                    "export_latest_versions": export_latest_versions,
                    "run_start_date": run_start_date,
                    "export_permissions": export_permissions,
                    "task_index": i,
                    "num_tasks": num_tasks,
                    "run_timestamp": "{{job.start_time.iso_date}}-Export-jobid-{{job.id}}",
                    "jobrunid": "jobrunid-{{job.run_id}}"
                }
            }
        }
        tasks.append(task)

    job_json = {
        "name": "Export_All_Models",
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
