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
# MAGIC * Destination base folder - Base output directory to which the model name will be appended to.
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
output_dir += f"/{model_name}"

dbutils.widgets.dropdown("3. Export source tags","no",["yes","no"])
export_source_tags = dbutils.widgets.get("3. Export source tags") == "yes"

notebook_formats = get_notebook_formats(4)

all_stages = [ "All", "Production", "Staging", "Archived", "None" ]
dbutils.widgets.multiselect("5. Stages", all_stages[0], all_stages)
stages = dbutils.widgets.get("5. Stages")
if stages == "All": 
    stages = None
else:
    stages = stages.split(",")
    if "" in stages: stages.remove("")

print("model_name:", model_name)
print("output_dir:", output_dir)
print("export_source_tags:", export_source_tags)
print("notebook_formats:", notebook_formats)
print("stages:", stages)

# COMMAND ----------

if len(model_name)==0: raise Exception("ERROR: 'Model' widget is required")
if len(output_dir)==0: raise Exception("ERROR: 'Destination base folder' widget is required")
  
import mlflow

# COMMAND ----------

# MAGIC %md ### Display MLflow UI URI of Registered Model

# COMMAND ----------

display_registered_model_uri(model_name)

# COMMAND ----------

# MAGIC %md ### Remove any previous exported model data
# MAGIC 
# MAGIC Note: may be a bit finicky (S3 eventual consistency). Just try the remove again if subsequent export fails.

# COMMAND ----------

dbutils.fs.rm(output_dir, True)
dbutils.fs.mkdirs(output_dir)

# COMMAND ----------

# MAGIC %md ### Export the model

# COMMAND ----------

from mlflow_export_import.model.export_model import ModelExporter
exporter = ModelExporter(mlflow.tracking.MlflowClient(), export_source_tags, notebook_formats, stages)
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