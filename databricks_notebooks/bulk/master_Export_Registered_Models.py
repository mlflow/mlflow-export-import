# Databricks notebook source
import requests
import json

# COMMAND ----------

dbutils.widgets.text("01. Models", "") 
models = dbutils.widgets.get("01. Models")

dbutils.widgets.text("02. Output directory", "/Workspace/Users/birbal.das@databricks.com/logs") 
output_dir = dbutils.widgets.get("02. Output directory")
output_dir = output_dir.replace("dbfs:","/dbfs")

dbutils.widgets.multiselect("03. Stages", "Production", ["Production","Staging","Archived","None"])
stages = dbutils.widgets.get("03. Stages")

dbutils.widgets.dropdown("04. Export latest versions","no",["yes","no"])
export_latest_versions = dbutils.widgets.get("04. Export latest versions") == "yes"

dbutils.widgets.dropdown("05. Export all runs","no",["yes","no"])
export_all_runs = dbutils.widgets.get("05. Export all runs") == "yes"

dbutils.widgets.dropdown("06. Export permissions","no",["yes","no"])
export_permissions = dbutils.widgets.get("06. Export permissions") == "yes"

dbutils.widgets.dropdown("07. Export deleted runs","no",["yes","no"])
export_deleted_runs = dbutils.widgets.get("07. Export deleted runs") == "yes"

dbutils.widgets.dropdown("08. Export version MLflow model","no",["yes","no"]) # TODO
export_version_model = dbutils.widgets.get("08. Export version MLflow model") == "yes"

# notebook_formats = get_notebook_formats("09")

dbutils.widgets.multiselect("09. Notebook formats", "SOURCE", [ "SOURCE", "DBC", "HTML", "JUPYTER" ])
notebook_formats = dbutils.widgets.get("09. Notebook formats")

dbutils.widgets.dropdown("10. Use threads","no",["yes","no"])
use_threads = dbutils.widgets.get("10. Use threads") == "yes"


dbutils.widgets.text("11. num_tasks", "") 
num_tasks = dbutils.widgets.get("11. num_tasks")


import os
os.environ["OUTPUT_DIR"] = output_dir

print("models:", models)
print("output_dir:", output_dir)
print("stages:", stages)
print("export_latest_versions:", export_latest_versions)
print("export_all_runs:", export_all_runs)
print("export_permissions:", export_permissions)
print("export_deleted_runs:", export_deleted_runs)
print("export_version_model:", export_version_model)
print("notebook_formats:", notebook_formats)
print("use_threads:", use_threads)
print("num_tasks:", num_tasks)

# COMMAND ----------

DATABRICKS_INSTANCE=dbutils.notebook.entry_point.getDbutils().notebook().getContext().tags().get('browserHostName').getOrElse(None)
DATABRICKS_INSTANCE = f"https://{DATABRICKS_INSTANCE}"
DATABRICKS_TOKEN = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().getOrElse(None)

driver_node_type = "Standard_D4ds_v5"
worker_node_type = "Standard_D4ds_v5"

def create_multi_task_job_json(models, output_dir, stages, export_latest_versions, export_all_runs, export_permissions, export_deleted_runs, export_version_model, notebook_formats, use_threads, num_tasks):
    tasks = []


    if models.lower() == "all" or models.endswith(".txt"):
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
                        "notebook_path": "/Workspace/Users/birbal.das@databricks.com/bir-mlflow-export-import/databricks_notebooks/bulk/Export_Registered_Models",
                        "base_parameters": {
                                "models" : models,
                                "output_dir" : output_dir,
                                "stages" : stages,
                                "export_latest_versions" : export_latest_versions,
                                "export_all_runs" : export_all_runs,
                                "export_permissions" : export_permissions,
                                "export_deleted_runs" : export_deleted_runs,
                                "export_version_model" : export_version_model,
                                "notebook_formats" : notebook_formats,
                                "use_threads" : use_threads,
                                "task_index": i,
                                "num_tasks" : num_tasks,
                                "run_timestamp" : "{{job.start_time.iso_date}}-jobid-{{job.id}}-jobrunid-{{job.run_id}}"
                        }
                    }
                }
                tasks.append(task)
    else:
            task = {
                    "task_key": f"task",
                    "description": f"Bir Task for param1 ",
                    "new_cluster": {
                        "spark_version": "15.4.x-cpu-ml-scala2.12",
                        "node_type_id": worker_node_type,
                        "driver_node_type_id": driver_node_type,
                        "num_workers": 1,
                        "data_security_mode": "SINGLE_USER",
                        "runtime_engine": "STANDARD"
                    },
                    "notebook_task": {
                        "notebook_path": "/Workspace/Users/birbal.das@databricks.com/bir-mlflow-export-import/databricks_notebooks/bulk/Export_Registered_Models",
                        "base_parameters": {
                                "models" : models,
                                "output_dir" : output_dir,
                                "stages" : stages,
                                "export_latest_versions" : export_latest_versions,
                                "export_all_runs" : export_all_runs,
                                "export_permissions" : export_permissions,
                                "export_deleted_runs" : export_deleted_runs,
                                "export_version_model" : export_version_model,
                                "notebook_formats" : notebook_formats,
                                "use_threads" : use_threads,
                                "task_index": "-1",
                                "num_tasks" : "-1",
                                "run_timestamp" : "{{job.start_time.iso_date}}-jobid-{{job.id}}-jobrunid-{{job.run_id}}"
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
    job_payload = create_multi_task_job_json(models, output_dir, stages, export_latest_versions, export_all_runs, export_permissions, export_deleted_runs, export_version_model, notebook_formats, use_threads, num_tasks)

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
