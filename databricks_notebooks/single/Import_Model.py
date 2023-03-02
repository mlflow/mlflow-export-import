# Databricks notebook source
# MAGIC %md ### Import Registered Model
# MAGIC 
# MAGIC ##### Overview
# MAGIC 
# MAGIC * Import a registered model from a folder.
# MAGIC * See notebook [Export_Model]($Export_Model).
# MAGIC 
# MAGIC ##### Widgets
# MAGIC * Model - new registered model name.
# MAGIC * Experiment name - contains runs created for model versions.
# MAGIC * Input directory - Input directory containing the exported model.
# MAGIC * Delete model - delete model and its versions before importing.
# MAGIC 
# MAGIC #### Limitations
# MAGIC * There is a bug where you cannot create a model with the same name as a deleted model.
# MAGIC 
# MAGIC #### Setup
# MAGIC * See Setup in [README]($./_README).

# COMMAND ----------

# MAGIC %run ./Common

# COMMAND ----------

dbutils.widgets.text("1. Model name", "") 
model_name = dbutils.widgets.get("1. Model name")

dbutils.widgets.text("2. Destination experiment name", "") 
experiment_name = dbutils.widgets.get("2. Destination experiment name")

dbutils.widgets.text("3. Input directory", "") 
input_dir = dbutils.widgets.get("3. Input directory")

dbutils.widgets.dropdown("4. Delete model","no",["yes","no"])
delete_model = dbutils.widgets.get("4. Delete model") == "yes"

import os
os.environ["INPUT_DIR"] = input_dir.replace("dbfs:","/dbfs")

print("model_name:", model_name)
print("input_dir:", input_dir)
print("experiment_name:", experiment_name)
print("delete_model:", delete_model)

# COMMAND ----------

assert_widget(model_name, "1. Model name")
assert_widget(experiment_name, "2. Destination experiment name")
assert_widget(input_dir, "3. Input directory")

# COMMAND ----------

# MAGIC %md ### Display model files to be imported

# COMMAND ----------

# MAGIC %sh ls -l $INPUT_DIR

# COMMAND ----------

# MAGIC %sh cat $INPUT_DIR/model.json

# COMMAND ----------

# MAGIC %md ### Import model

# COMMAND ----------

from mlflow_export_import.model.import_model import ModelImporter
importer = ModelImporter(mlflow.client.MlflowClient())
importer.import_model(model_name, 
                      input_dir = input_dir, 
                      experiment_name = experiment_name, 
                      delete_model = delete_model)

# COMMAND ----------

# MAGIC %md ### Display MLflow UI URIs

# COMMAND ----------

display_registered_model_uri(model_name)

# COMMAND ----------

display_experiment_uri(experiment_name)