# Databricks notebook source
# MAGIC %md ## Export Models
# MAGIC 
# MAGIC Export specified models, their version runs and the experiments that the runs belong to.
# MAGIC 
# MAGIC Widgets
# MAGIC * `1. Models` - comma seperated registered model names to be exported. `all` will export all models.
# MAGIC * `2. Output base directory`
# MAGIC * `3. Stages` - stages to be exported.
# MAGIC * `4. Export all runs` - export all runs of experiment that is linked to a registered model.
# MAGIC * `5. Notebook formats`
# MAGIC * `6. Use threads`
# MAGIC 
# MAGIC See: https://github.com/mlflow/mlflow-export-import/blob/master/README_bulk.md#registered-models.

# COMMAND ----------

# MAGIC %run ./Common

# COMMAND ----------

dbutils.widgets.text("1. Models", "") 
models = dbutils.widgets.get("1. Models")

dbutils.widgets.text("2. Output base directory", "dbfs:/mnt/andre-work/exim/experiments") 
output_dir = dbutils.widgets.get("2. Output base directory")
output_dir = output_dir.replace("dbfs:","/dbfs")

all_formats = [ "SOURCE", "DBC", "HTML", "JUPYTER" ]
dbutils.widgets.multiselect("3. Notebook formats",all_formats[0],all_formats)
notebook_formats = dbutils.widgets.get("3. Notebook formats")

dbutils.widgets.dropdown("4. Export all runs","no",["yes","no"])
export_all_runs = dbutils.widgets.get("4. Export all runs") == "yes"

dbutils.widgets.multiselect("5. Stages", "Production", ["Production","Staging","Archived","None"])
stages = dbutils.widgets.get("5. Stages")

dbutils.widgets.dropdown("6. Use threads","no",["yes","no"])
use_threads = dbutils.widgets.get("6. Use threads") == "yes"

export_notebook_revision = False
export_all_runs = False

import os
os.environ["OUTPUT_DIR"] = output_dir

print("models:", models)
print("output_dir:", output_dir)
print("stages:", stages)
print("notebook_formats:", notebook_formats)
print("export_all_runs:", export_all_runs)
print("use_threads:", use_threads)

# COMMAND ----------

assert_widget(models, "1. Models")
assert_widget(output_dir, "2. Output base directory")

# COMMAND ----------

# MAGIC %md ### Export models

# COMMAND ----------

from mlflow_export_import.bulk.export_models import export_models
import mlflow

export_models(
    mlflow_client = mlflow.client.MlflowClient(), 
    model_names = models, 
    output_dir = output_dir,
    notebook_formats = notebook_formats,
    stages = stages, 
    export_all_runs = export_all_runs,
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
