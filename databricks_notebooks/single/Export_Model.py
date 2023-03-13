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
# MAGIC * `3. Notebook formats` - Notebook formats to export.
# MAGIC * `4. Stages` - Model version stages to export.
# MAGIC * `5. Export latest versions`

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

notebook_formats = get_notebook_formats(3) # widget "3.Notebook formats"

all_stages = [ "All", "Production", "Staging", "Archived", "None" ]
dbutils.widgets.multiselect("4. Stages", all_stages[0], all_stages)
stages = dbutils.widgets.get("4. Stages")
if stages == "All": 
    stages = None
else:
    stages = stages.split(",")
    if "" in stages: stages.remove("")

dbutils.widgets.dropdown("5. Export latest versions","no",["yes","no"])
export_latest_versions = dbutils.widgets.get("5. Export latest versions") == "yes"

print("model_name:", model_name)
print("output_dir:", output_dir)
print("notebook_formats:", notebook_formats)
print("stages:", stages)
print("export_latest_versions:", export_latest_versions)

# COMMAND ----------

assert_widget(model_name, "1. Model")
assert_widget(output_dir, "2. Output base directory")

output_dir += f"/{model_name}"

import mlflow
print("output_dir:", output_dir)

# COMMAND ----------

# MAGIC %md ### Display MLflow UI URI of Registered Model

# COMMAND ----------

display_registered_model_uri(model_name)

# COMMAND ----------

# MAGIC %md ### Export the model

# COMMAND ----------

from mlflow_export_import.model.export_model import export_model

export_model(
    model_name = model_name, 
    output_dir = output_dir,
    stages = stages,
    #versions = versions, # TODO
    export_latest_versions = export_latest_versions,
    notebook_formats = notebook_formats, 
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