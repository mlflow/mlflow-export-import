# Databricks notebook source
# MAGIC %md ## Import Run
# MAGIC 
# MAGIC Import run from the folder that was created by the [Export_Run]($Export_Run) notebook.
# MAGIC 
# MAGIC #### Widgets
# MAGIC * `1. Destination experiment name` - Import run into this experiment. Will create if it doesn't exist.
# MAGIC * `2. Input directory` - Input directory containing an exported run.

# COMMAND ----------

# MAGIC %md ### Include setup

# COMMAND ----------

# MAGIC %run ./Common

# COMMAND ----------

# MAGIC %md ### Widget setup

# COMMAND ----------

dbutils.widgets.text("1. Destination experiment name", "") 
experiment_name = dbutils.widgets.get("1. Destination experiment name")

dbutils.widgets.text("2. Input directory", "") 
input_dir = dbutils.widgets.get("2. Input directory")

print("input_dir:",input_dir)
print("experiment_name:",experiment_name)

# COMMAND ----------

assert_widget(experiment_name, "1. Destination experiment name")
assert_widget(input_dir, "2. Input base directory")

# COMMAND ----------

# MAGIC %md ### Import Run

# COMMAND ----------

import mlflow
from mlflow_export_import.run.import_run import RunImporter

importer = RunImporter(
    mlflow_client = mlflow.client.MlflowClient()
)
run, _ = importer.import_run(
    experiment_name = experiment_name, 
    input_dir = input_dir
)
run.info.run_id

# COMMAND ----------

# MAGIC %md ### Display run link in MLflow UI

# COMMAND ----------

display_run_uri(run.info.run_id)
