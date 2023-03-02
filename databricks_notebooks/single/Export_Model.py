# Databricks notebook source
# MAGIC %md ### Export Registered Model
# MAGIC 
# MAGIC ##### Overview
# MAGIC * Export a registered model and all the runs associated with its latest versions to a DBFS folder.
# MAGIC * Output file `model.json` contains model metadata.
# MAGIC * Each run and its artifacts are stored as a sub-directory.
# MAGIC 
# MAGIC #### Output folder structure
# MAGIC 
# MAGIC ```
# MAGIC +-model.json
# MAGIC +-d2309e6c74dc4679b576a37abf6b6af8/
# MAGIC | +-run.json
# MAGIC | +-artifacts/
# MAGIC |   +-plot.png
# MAGIC |   +-sklearn-model/
# MAGIC |   | +-model.pkl
# MAGIC |   | +-conda.yaml
# MAGIC |   | +-MLmodel
# MAGIC ```
# MAGIC 
# MAGIC ##### Widgets
# MAGIC * Model - Registered model name.
# MAGIC * Output base directory - Base output directory to which the model name will be appended to.
# MAGIC * Notebook formats to export.
# MAGIC * Stages to export.
# MAGIC 
# MAGIC #### Setup
# MAGIC * See Setup in [README]($./_README).

# COMMAND ----------

# MAGIC %md ### Setup

# COMMAND ----------

# MAGIC %run ./Common

# COMMAND ----------

dbutils.widgets.text("1. Model", "") 
model_name = dbutils.widgets.get("1. Model")

dbutils.widgets.text("2. Output base directory", "") 
output_dir = dbutils.widgets.get("2. Output base directory")

notebook_formats = get_notebook_formats(3)

all_stages = [ "All", "Production", "Staging", "Archived", "None" ]
dbutils.widgets.multiselect("4. Stages", all_stages[0], all_stages)
stages = dbutils.widgets.get("4. Stages")
if stages == "All": 
    stages = None
else:
    stages = stages.split(",")
    if "" in stages: stages.remove("")

print("model_name:", model_name)
print("output_dir:", output_dir)
print("notebook_formats:", notebook_formats)
print("stages:", stages)

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

from mlflow_export_import.model.export_model import ModelExporter
exporter = ModelExporter(
    mlflow.client.MlflowClient(),
    notebook_formats = notebook_formats, 
    stages = stages)
exporter.export_model(model_name, output_dir)

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