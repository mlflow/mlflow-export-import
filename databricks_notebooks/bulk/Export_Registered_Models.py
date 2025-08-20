# Databricks notebook source
# MAGIC %md ## Export Registered Models
# MAGIC
# MAGIC Export specified models, their version runs and the experiments that the runs belong to.
# MAGIC
# MAGIC Widgets
# MAGIC * `01. Models` - comma seperated registered model names to be exported. `all` will export all models. Or filename (ending with .txt) with model names.
# MAGIC * `02. Output directory` - shared directory between source and destination workspaces.
# MAGIC * `03. Stages` - stages to be exported.
# MAGIC * `04. Export latest versions` - expor all or just the "latest" versions.
# MAGIC * `05. Export all runs` - export all runs of an experiment that are linked to a registered model.
# MAGIC * `06. Export permissions` - export Databricks permissions.
# MAGIC * `07. Export deleted runs`
# MAGIC * `08. Export version MLflow model`
# MAGIC * `08. Notebook formats`
# MAGIC * `10. Use threads`
# MAGIC
# MAGIC See: https://github.com/mlflow/mlflow-export-import/blob/master/README_bulk.md#registered-models.

# COMMAND ----------

# MAGIC %run ./Common

# COMMAND ----------

from mlflow_export_import.bulk import config
import time
import os

# COMMAND ----------

model_file_name = dbutils.widgets.get("model_file_name")

output_dir = dbutils.widgets.get("output_dir")
output_dir = output_dir.replace("dbfs:","/dbfs")

stages = dbutils.widgets.get("stages")

export_latest_versions = dbutils.widgets.get("export_latest_versions") == "true"

export_permissions = dbutils.widgets.get("export_permissions") == "true"

export_deleted_runs = dbutils.widgets.get("export_deleted_runs") == "true"

task_index = int(dbutils.widgets.get("task_index"))

num_tasks = int(dbutils.widgets.get("num_tasks"))

run_timestamp = dbutils.widgets.get("run_timestamp")

dbutils.widgets.text("jobrunid", "")
jobrunid = dbutils.widgets.get("jobrunid")

print("model_file_name:", model_file_name)
print("output_dir:", output_dir)
print("stages:", stages)
print("export_latest_versions:", export_latest_versions)
print("export_permissions:", export_permissions)
print("export_deleted_runs:", export_deleted_runs)
print("task_index:", task_index)
print("num_tasks:", num_tasks)
print("run_timestamp:", run_timestamp)
print("jobrunid:", jobrunid)

# COMMAND ----------

log_path=f"/tmp/my.log"
log_path

# COMMAND ----------

config.log_path=log_path

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

# MAGIC %md ### Export models

# COMMAND ----------

from mlflow_export_import.bulk.export_models import export_models

export_models(
    model_names = model_file_name, 
    output_dir = output_dir,
    stages = stages, 
    export_latest_versions = export_latest_versions,
    export_all_runs = True,
    export_version_model = False,
    export_permissions = export_permissions,
    export_deleted_runs = export_deleted_runs, 
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

# COMMAND ----------

# MAGIC %md ### Display exported files

# COMMAND ----------

# MAGIC %sh 
# MAGIC echo $OUTPUT_DIR
# MAGIC ls -l $OUTPUT_DIR

# COMMAND ----------

# MAGIC %sh cat $OUTPUT_DIR/manifest.json

# COMMAND ----------

# MAGIC %sh ls -l $OUTPUT_DIR/models

# COMMAND ----------

# MAGIC %sh cat $OUTPUT_DIR/models/models.json

# COMMAND ----------

# MAGIC %sh ls -l $OUTPUT_DIR/experiments

# COMMAND ----------

# MAGIC %sh cat $OUTPUT_DIR/experiments/experiments.json

# COMMAND ----------


