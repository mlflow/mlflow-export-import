# Databricks notebook source
# MAGIC %md ## Export All
# MAGIC
# MAGIC Export all the MLflow registered models and all experiments of a tracking server.
# MAGIC
# MAGIC **Widgets**
# MAGIC * `1. Output directory` - shared directory between source and destination workspaces.
# MAGIC * `2. Stages` - comma seperated stages to be exported.
# MAGIC * `3. Export latest versions` - export all or just the "latest" versions.
# MAGIC * `4. Run start date` - Export runs after this UTC date (inclusive). Example: `2023-04-05`.
# MAGIC * `5. Export permissions` - export Databricks permissions.
# MAGIC * `6. Export deleted runs`
# MAGIC * `7. Export version MLflow model`
# MAGIC * `8. Notebook formats`
# MAGIC * `9. Use threads`

# COMMAND ----------

# MAGIC %run ./Common

# COMMAND ----------

from mlflow_export_import.bulk import config
import time
import os

# COMMAND ----------


output_dir = dbutils.widgets.get("output_dir")
output_dir = dbutils.widgets.get("output_dir")
output_dir = output_dir.replace("dbfs:","/dbfs")

dbutils.widgets.multiselect("stages", "Production", ["Production","Staging","Archived","None"])
stages = dbutils.widgets.get("stages")

dbutils.widgets.dropdown("export_latest_versions","false",["true","false"])
export_latest_versions = dbutils.widgets.get("export_latest_versions") == "true"

dbutils.widgets.text("run_start_date", "") 
run_start_date = dbutils.widgets.get("run_start_date")

dbutils.widgets.dropdown("export_permissions","false",["true","false"])
export_permissions = dbutils.widgets.get("export_permissions") == "true"

dbutils.widgets.text("task_index", "")
task_index = int(dbutils.widgets.get("task_index"))

dbutils.widgets.text("num_tasks", "")
num_tasks = int(dbutils.widgets.get("num_tasks"))

dbutils.widgets.text("run_timestamp", "")
run_timestamp = dbutils.widgets.get("run_timestamp")

dbutils.widgets.text("jobrunid", "")
jobrunid = dbutils.widgets.get("jobrunid")
 
if run_start_date=="": run_start_date = None

print("output_dir:", output_dir)
print("stages:", stages)
print("export_latest_versions:", export_latest_versions)
print("run_start_date:", run_start_date)
print("export_permissions:", export_permissions)
print("task_index:", task_index)
print("num_tasks:", num_tasks)
print("run_timestamp:", run_timestamp)
print("jobrunid:", jobrunid)

# COMMAND ----------

checkpoint_dir_experiment = os.path.join(output_dir, run_timestamp,"checkpoint", "experiments")
try:
    if not os.path.exists(checkpoint_dir_experiment):
        os.makedirs(checkpoint_dir_experiment, exist_ok=True)
        print(f"checkpoint_dir_experiment: created {checkpoint_dir_experiment}")
except Exception as e:
    raise Exception(f"Failed to create directory {checkpoint_dir_experiment}: {e}")

# COMMAND ----------

checkpoint_dir_model = os.path.join(output_dir, run_timestamp,"checkpoint", "models")
try:
    if not os.path.exists(checkpoint_dir_model):
        os.makedirs(checkpoint_dir_model, exist_ok=True)
        print(f"checkpoint_dir_model: created {checkpoint_dir_model}")
except Exception as e:
    raise Exception(f"Failed to create directory {checkpoint_dir_model}: {e}")

# COMMAND ----------

output_dir = os.path.join(output_dir, run_timestamp, jobrunid, str(task_index))
output_dir

# COMMAND ----------

log_path=f"/tmp/my.log"
log_path

# COMMAND ----------

config.log_path=log_path
config.export_or_import="export"

# COMMAND ----------

from mlflow_export_import.bulk.export_all import export_all

export_all(
    output_dir = output_dir, 
    stages = stages,
    export_latest_versions = export_latest_versions,
    run_start_time = run_start_date,
    export_permissions = export_permissions,
    export_deleted_runs = False,
    export_version_model = False,
    notebook_formats = ['SOURCE'], 
    use_threads = True,
    task_index = task_index,
    num_tasks = num_tasks,
    checkpoint_dir_experiment = checkpoint_dir_experiment,
    checkpoint_dir_model = checkpoint_dir_model
)

# COMMAND ----------

time.sleep(10)

# COMMAND ----------

# MAGIC %sh cat /tmp/my.log

# COMMAND ----------

dbfs_log_path = f"{output_dir}/export_all_{task_index}.log"
if dbfs_log_path.startswith("/Workspace"):
    dbfs_log_path=dbfs_log_path.replace("/Workspace","file:/Workspace") 
dbfs_log_path = dbfs_log_path.replace("/dbfs","dbfs:")
dbfs_log_path

# COMMAND ----------


dbutils.fs.cp(f"file:{log_path}", dbfs_log_path)

# COMMAND ----------

print(dbutils.fs.head(dbfs_log_path))
