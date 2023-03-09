# Databricks notebook source
# MAGIC %md ### Import Experiment
# MAGIC 
# MAGIC **Widgets**
# MAGIC * Input directory - DBFS input directory containing an exported experiment.
# MAGIC * Destination experiment name - Will create if it doesn't exist.
# MAGIC 
# MAGIC #### Setup
# MAGIC * See the Setup section in [README]($./_README).

# COMMAND ----------

# MAGIC %run ./Common

# COMMAND ----------


dbutils.widgets.text("1. Destination experiment name", "") 
experiment_name = dbutils.widgets.get("1. Destination experiment name")

dbutils.widgets.text("2. Input directory", "") 
input_dir = dbutils.widgets.get("2. Input directory")

print("input_dir:",input_dir)
print("experiment_name:",experiment_name)

# COMMAND ----------

assert_widget(experiment_name, "1. Destination experiment name")
assert_widget(input_dir, "2. Input directory")

# COMMAND ----------

from mlflow_export_import.experiment.import_experiment import ExperimentImporter

importer = ExperimentImporter(
    mlflow_client = mlflow.client.MlflowClient()
)
importer.import_experiment(
    experiment_name = experiment_name, 
    input_dir = input_dir
)

# COMMAND ----------

display_experiment_uri(experiment_name)
