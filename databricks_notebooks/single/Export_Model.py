# Databricks notebook source
# MAGIC %md ### Export Registered Model
# MAGIC 
# MAGIC ##### Overview
# MAGIC * Export a registered model and all the runs associated with its latest versions to a DBFS folder.
# MAGIC * Output file `model.json` contains model metadata.
# MAGIC * Each run and its artifacts are stored as a sub-directory.
# MAGIC 
# MAGIC ##### Widgets
# MAGIC * `1. Model` - Registered model name to export.
# MAGIC * `2. Output base directory` - Base output directory to which the model name will be appended to.
# MAGIC * `3. Stages` - Model version stages to export.
# MAGIC * `4. Export latest versions`
# MAGIC * `5. Versions` - comma delimited version numbers to export.
# MAGIC * `6. Export permissions` - Export Databricks permissions.
# MAGIC * `7. Notebook formats` - Notebook formats to export.

# COMMAND ----------

# MAGIC %md ### Include setup

# COMMAND ----------

# MAGIC %run ./Common

# COMMAND ----------

# MAGIC %md ### Widget setup

# COMMAND ----------

dbutils.widgets.text("1. Model", "") 
model_name = dbutils.widgets.get("1. Model")

dbutils.widgets.text("2. Output base directory", "") 
output_dir = dbutils.widgets.get("2. Output base directory")

all_stages = [ "All", "Production", "Staging", "Archived", "None" ]
dbutils.widgets.multiselect("3. Stages", all_stages[0], all_stages)
stages = dbutils.widgets.get("3. Stages")
if stages == "All": 
    stages = None
else:
    stages = stages.split(",")
    if "" in stages: stages.remove("")

dbutils.widgets.dropdown("4. Export latest versions","no",["yes","no"])
export_latest_versions = dbutils.widgets.get("4. Export latest versions") == "yes"

dbutils.widgets.text("5. Versions", "") 
versions = dbutils.widgets.get("5. Versions")
versions = versions.split(",") if versions else []

dbutils.widgets.dropdown("6. Export permissions","no",["yes","no"])
export_permissions = dbutils.widgets.get("6. Export permissions") == "yes"

notebook_formats = get_notebook_formats(7) # widget "7. Notebook formats"

print("model_name:", model_name)
print("output_dir:", output_dir)
print("stages:", stages)
print("export_latest_versions:", export_latest_versions)
print("export_permissions:", export_permissions)
print("notebook_formats:", notebook_formats)
print("versions:", versions)

# COMMAND ----------

assert_widget(model_name, "1. Model")
assert_widget(output_dir, "2. Output base directory")

output_dir += f"/{model_name}"

import mlflow
print("output_dir:", output_dir)

# COMMAND ----------

# MAGIC %md ### Export the model

# COMMAND ----------

from mlflow_export_import.model.export_model import export_model

export_model(
    model_name = model_name, 
    output_dir = output_dir,
    stages = stages,
    versions = versions,
    export_latest_versions = export_latest_versions,
    export_permissions = export_permissions,
    notebook_formats = notebook_formats
)

# COMMAND ----------

# MAGIC %md ### Display  exported model files

# COMMAND ----------

import os
output_dir = output_dir.replace("dbfs:","/dbfs")
os.environ['OUTPUT_DIR'] = output_dir

# COMMAND ----------

# MAGIC %sh echo $OUTPUT_DIR

# COMMAND ----------

# MAGIC %sh ls -l $OUTPUT_DIR

# COMMAND ----------

# MAGIC %sh cat $OUTPUT_DIR/model.json
