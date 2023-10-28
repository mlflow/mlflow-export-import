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

dbutils.widgets.text("01. Models", "") 
models = dbutils.widgets.get("01. Models")

dbutils.widgets.text("02. Output directory", "dbfs:/mnt/andre-work/exim/experiments") 
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

notebook_formats = get_notebook_formats("09")

dbutils.widgets.dropdown("10. Use threads","no",["yes","no"])
use_threads = dbutils.widgets.get("10. Use threads") == "yes"

export_notebook_revision = False
export_all_runs = False

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

# COMMAND ----------

assert_widget(models, "1. Models")
assert_widget(output_dir, "2. Output directory")

# COMMAND ----------

# MAGIC %md ### Export models

# COMMAND ----------

from mlflow_export_import.bulk.export_models import export_models

export_models(
    model_names = models, 
    output_dir = output_dir,
    stages = stages, 
    export_latest_versions = export_latest_versions,
    export_all_runs = export_all_runs,
    export_version_model = export_version_model,
    export_permissions = export_permissions,
    export_deleted_runs = export_deleted_runs, 
    notebook_formats = notebook_formats,
    use_threads = use_threads
)

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
