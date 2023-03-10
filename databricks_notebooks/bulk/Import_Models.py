# Databricks notebook source
# MAGIC %md ## Import Models
# MAGIC 
# MAGIC Widgets
# MAGIC * `1. Input directory` - directory of exported experiments
# MAGIC * `2. Use threads` - use multi-threaded import
# MAGIC * `3. Delete model` - delete the current contents of model
# MAGIC 
# MAGIC See https://github.com/mlflow/mlflow-export-import/blob/master/README_collection.md#Import-registered-models

# COMMAND ----------

# MAGIC %run ./Common

# COMMAND ----------

dbutils.widgets.text("1. Input directory", "") 
input_dir = dbutils.widgets.get("1. Input directory")
input_dir = input_dir.replace("dbfs:","/dbfs")

dbutils.widgets.dropdown("2. Delete model","no",["yes","no"])
delete_model = dbutils.widgets.get("2. Delete model") == "yes"

dbutils.widgets.dropdown("3. Use threads","no",["yes","no"])
use_threads = dbutils.widgets.get("3. Use threads") == "yes"

print("input_dir:", input_dir)
print("delete_model:", delete_model)
print("use_threads:", use_threads)

# COMMAND ----------

assert_widget(input_dir, "1. Input directory")

# COMMAND ----------

from mlflow_export_import.bulk.import_models import import_all
import mlflow

import_all(
    mlflow_client = mlflow_client,
    input_dir = input_dir,
    delete_model = delete_model,
    use_threads = use_threads
  )
