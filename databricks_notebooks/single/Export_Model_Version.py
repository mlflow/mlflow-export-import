# Databricks notebook source
# MAGIC %md ### Export Model Version
# MAGIC
# MAGIC ##### Overview
# MAGIC * Export a model version and its run.
# MAGIC
# MAGIC ##### Widgets
# MAGIC * `1. Model` - Registered model name.
# MAGIC * `2. Version` - Model  version.
# MAGIC * `3. Output directory` - Output directory.
# MAGIC * `4. Export version MLflow model` - Export a model version's "cached" registry MLflow model (clone of run's MLflow model).
# MAGIC * `5. Notebook formats` - Notebook formats to export.

# COMMAND ----------

# MAGIC %md ### Include setup

# COMMAND ----------

# MAGIC %run ./Common

# COMMAND ----------

# MAGIC %md ### Widget setup

# COMMAND ----------

dbutils.widgets.text("1. Model name", "") 
model_name = dbutils.widgets.get("1. Model name")

dbutils.widgets.text("2. Model version", "") 
version = dbutils.widgets.get("2. Model version")

dbutils.widgets.text("3. Output directory", "") 
output_dir = dbutils.widgets.get("3. Output directory")

dbutils.widgets.dropdown("4. Export version MLflow model","no",["yes","no"])
export_version_model = dbutils.widgets.get("4. Export version MLflow model") == "yes"

notebook_formats = get_notebook_formats(5) # widget "7. Notebook formats"

print("model_name:", model_name)
print("version:", version)
print("output_dir:", output_dir)
print("export_version_model:", export_version_model)
print("notebook_formats:", notebook_formats)

# COMMAND ----------

assert_widget(model_name, "1. Model name")
assert_widget(model_name, "2. Model version")
assert_widget(output_dir, "3. Output directory")

# COMMAND ----------

# MAGIC %md ### Turn on Unity Catalog mode if necessary

# COMMAND ----------

activate_unity_catalog(model_name)

# COMMAND ----------

# MAGIC %md ### Display model UI link

# COMMAND ----------

display_registered_model_uri(model_name)

# COMMAND ----------

# MAGIC %md ### Export the model version

# COMMAND ----------

from mlflow_export_import.model_version.export_model_version import export_model_version

export_model_version(
    model_name = model_name, 
    version = version, 
    output_dir = output_dir,
    export_version_model = export_version_model,
    notebook_formats = notebook_formats
)

# COMMAND ----------

# MAGIC %md ### Display  exported files

# COMMAND ----------

import os
output_dir = mk_local_path(output_dir)
os.environ['OUTPUT_DIR'] = output_dir

# COMMAND ----------

# MAGIC %sh echo $OUTPUT_DIR

# COMMAND ----------

# MAGIC %sh ls -l $OUTPUT_DIR

# COMMAND ----------

# MAGIC %sh 
# MAGIC cat $OUTPUT_DIR/model_version.json
