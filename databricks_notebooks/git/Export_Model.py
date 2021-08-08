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
# MAGIC * See Setup in [README]($00_README_Export_Import).

# COMMAND ----------

# MAGIC %md ### Setup

# COMMAND ----------

dbutils.widgets.text(" Model", "") 
model_name = dbutils.widgets.get(" Model")

dbutils.widgets.text("Destination base folder", "") 
output_dir = dbutils.widgets.get("Destination base folder")
output_dir += f"/{model_name}"

model_name, output_dir

# COMMAND ----------

if len(model_name)==0: raise Exception("ERROR: Model is required")
if len(output_dir)==0: raise Exception("ERROR: DBFS destination is required")
  
import mlflow

# COMMAND ----------

# MAGIC %md ### Display MLflow UI URI of Registered Model

# COMMAND ----------

# MAGIC %run ./Common

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
exporter = ModelExporter()
exporter.export_model(output_dir, model_name)

# COMMAND ----------

# MAGIC %sh ls -l /dbfs/mnt/andre-work/exim/models/andre_02_Sklearn_Train_Predict/ec7bc29448b54ea497cd88dbcd46a155/run.json

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

# COMMAND ----------

# MAGIC %md #### Display run information

# COMMAND ----------

find_run_dir(output_dir, "RUN_DIR", "manifest.json")

# COMMAND ----------

# MAGIC %sh echo $RUN_DIR

# COMMAND ----------

# MAGIC %sh ls -l $RUN_DIR

# COMMAND ----------

# MAGIC %sh  cat $RUN_DIR/run.json