# Databricks notebook source
# MAGIC %md ### Import Experiment
# MAGIC 
# MAGIC **Widgets**
# MAGIC * Input directory - DBFS input directory containing an exported experiment.
# MAGIC * Destination experiment name - Will create if it doesn't exist.
# MAGIC * Just peek - Just display manifest.json and do not import the experiment.
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

dbutils.widgets.dropdown("3. Just peek","no",["yes","no"])
just_peek = dbutils.widgets.get("3. Just peek") == "yes"

print("input_dir:",input_dir)
print("experiment_name:",experiment_name)
print("just_peek:",just_peek)

# COMMAND ----------

if len(input_dir)==0: raise Exception("ERROR: Input directory is required")
if len(experiment_name)==0: raise Exception("ERROR: Destination experiment name is required")

# COMMAND ----------

from mlflow_export_import.experiment.import_experiment import ExperimentImporter
from mlflow_export_import import peek_at_experiment

importer = ExperimentImporter(mlflow.tracking.MlflowClient())
peek_at_experiment(input_dir)

# COMMAND ----------

input_dir

# COMMAND ----------

 if not just_peek:
    if len(experiment_name)==0: raise Exception("ERROR: Destination Experiment Name is required")
    importer.import_experiment(experiment_name, input_dir)

# COMMAND ----------

display_experiment_uri(experiment_name)