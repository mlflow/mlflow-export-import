# Databricks notebook source
# MAGIC %md ### Import Experiment
# MAGIC 
# MAGIC **Widgets**
# MAGIC * DBFS input folder - Input directory containing an exported experiment.
# MAGIC * Destination experiment name - Will create if it doesn't exist.
# MAGIC * Just peek - Just display manifest.json and do not import the experiment.
# MAGIC 
# MAGIC #### Setup
# MAGIC * See Setup in [README]($00_README_Export_Import).

# COMMAND ----------

# MAGIC %run ./Common

# COMMAND ----------

dbutils.widgets.text("Destination experiment name", "") 
experiment_name = dbutils.widgets.get("Destination experiment name")

dbutils.widgets.text("DBFS input folder", "") 
input_dir = dbutils.widgets.get("DBFS input folder")

dbutils.widgets.dropdown("Import metadata tags","no",["yes","no"])
import_metadata_tags = dbutils.widgets.get("Import metadata tags") == "yes"

dbutils.widgets.dropdown("Just peek","no",["yes","no"])
just_peek = dbutils.widgets.get("Just peek") == "yes"

if len(input_dir)==0: raise Exception("ERROR: Input is required")
input_dir, experiment_name, import_metadata_tags, just_peek

# COMMAND ----------

from mlflow_export_import.experiment.import_experiment import ExperimentImporter
from mlflow_export_import import peek_at_experiment

importer = ExperimentImporter(import_metadata_tags=import_metadata_tags)
peek_at_experiment(input_dir)

# COMMAND ----------

 if not just_peek:
    if len(experiment_name)==0: raise Exception("ERROR: Destination Experiment Name is required")
    importer.import_experiment(experiment_name, input_dir)

# COMMAND ----------

display_experiment_uri(experiment_name)