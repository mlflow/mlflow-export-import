# Databricks notebook source
# MAGIC %md ## Import Run
# MAGIC 
# MAGIC Import run from folder that was created by [Export_Run]($Export_Run) notebook.
# MAGIC 
# MAGIC #### Widgets
# MAGIC * Destination experiment name - Import run into this experiment. Will create if it doesn't exist.
# MAGIC * Input folder - Input directory containing an exported run.
# MAGIC 
# MAGIC #### Setup
# MAGIC * See Setup in [README]($00_README_Export_Import).

# COMMAND ----------

# MAGIC %md ### Setup

# COMMAND ----------

dbutils.widgets.text("Destination experiment name", "") 
experiment_name = dbutils.widgets.get("Destination experiment name")

dbutils.widgets.text("Input folder", "") 
input_dir = dbutils.widgets.get("Input folder")

if len(input_dir)==0: raise Exception("ERROR: Input is required")
input_dir, experiment_name

print("input_dir:",input_dir)
print("experiment_name:",experiment_name)

# COMMAND ----------

# MAGIC %md ### Import Run

# COMMAND ----------

from mlflow_export_import.run.import_run import RunImporter
importer = RunImporter(import_mlflow_tags=False)
run, _ = importer.import_run(experiment_name, input_dir)
run.info.run_id

# COMMAND ----------

# MAGIC %md ### Display MLflow UI URIs

# COMMAND ----------

# MAGIC %run ./Common

# COMMAND ----------

display_run_uri(run.info.run_id)