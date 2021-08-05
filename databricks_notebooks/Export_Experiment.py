# Databricks notebook source
# MAGIC %md ### Export Experiment
# MAGIC 
# MAGIC ##### Overview
# MAGIC * Exports an experiment and its runs (artifacts too) to a DBFS directory.
# MAGIC * Output file `manifest.json` contains top-level experiment metadata.
# MAGIC * Each run and its artifacts are stored as a sub-directory.
# MAGIC * Notebooks also can be exported in several formats.
# MAGIC 
# MAGIC #### Output folder
# MAGIC ```
# MAGIC 
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
# MAGIC * Experiment ID or Name - Either the experiment ID or the name.
# MAGIC * DBFS destination - Base output directory to which the experiment ID will be appended to. All experiment data will be saved there.
# MAGIC * Log source metadata as tags such as:
# MAGIC   * mlflow_tools.export.experiment_name
# MAGIC   * mlflow_tools.export.experiment_id
# MAGIC   * mlflow_tools.export.experiment_name	
# MAGIC * Notebook formats:
# MAGIC   * Standard Databricks notebook formats such as SOURCE, HTML, JUPYTER, DBC. See [Databricks Export Format](https://docs.databricks.com/dev-tools/api/latest/workspace.html#notebookexportformat) documentation.
# MAGIC 
# MAGIC #### Setup
# MAGIC * See Setup in [README]($00_README_Export_Import).

# COMMAND ----------

# MAGIC %md ### Create and process widgets 

# COMMAND ----------

dbutils.widgets.text(" Experiment ID or Name", "") 
experiment_id_or_name = dbutils.widgets.get(" Experiment ID or Name")
 
dbutils.widgets.text("Destination base folder", "dbfs:/mnt/andre-work/exim/experiments") 
output_dir = dbutils.widgets.get("Destination base folder")

dbutils.widgets.dropdown("Export metadata tags","no",["yes","no"])
export_metadata_tags = dbutils.widgets.get("Export metadata tags") == "yes"

all_formats = [ "SOURCE", "DBC", "HTML", "JUPYTER" ]
dbutils.widgets.multiselect("Notebook formats",all_formats[0],all_formats)
formats = dbutils.widgets.get("Notebook formats")
formats = formats.split(",")
if "" in formats: formats.remove("")

experiment_id_or_name, output_dir, export_metadata_tags, formats

# COMMAND ----------

if len(experiment_id_or_name)==0: raise Exception("ERROR: Experiment ID or Name is required")
if len(output_dir)==0: raise Exception("ERROR: DBFS destination is required")
  
import mlflow
from mlflow_export_import.common import mlflow_utils 

experiment = mlflow_utils.get_experiment(mlflow.tracking.MlflowClient(), experiment_id_or_name)

output_dir = f"{output_dir}/{experiment.experiment_id}"

experiment.experiment_id, experiment.name, output_dir

# COMMAND ----------

# MAGIC %md ### Display MLflow UI URI of Experiment

# COMMAND ----------

# MAGIC %run ./Common

# COMMAND ----------

display_experiment_uri(experiment.name)

# COMMAND ----------

# MAGIC %md ### Remove any previous exported experiment data
# MAGIC 
# MAGIC Note: may be a bit finicky (S3 eventual consistency). Just try the remove again if subsequent export fails.

# COMMAND ----------

dbutils.fs.rm(output_dir, True)
dbutils.fs.rm(output_dir, False)

# COMMAND ----------

# MAGIC %md ### Export the experiment

# COMMAND ----------

from mlflow_export_import.experiment.export_experiment import ExperimentExporter

exporter = ExperimentExporter(notebook_formats=formats, 
                              export_metadata_tags=export_metadata_tags)
exporter.export_experiment(experiment.experiment_id, output_dir)

# COMMAND ----------

# MAGIC %md ### Display  exported experiment files

# COMMAND ----------

import os
output_dir = output_dir.replace("dbfs:","/dbfs")
os.environ['OUTPUT_DIR'] = output_dir
output_dir

# COMMAND ----------

# MAGIC %sh echo $OUTPUT_DIR

# COMMAND ----------

# MAGIC %sh ls -lR $OUTPUT_DIR

# COMMAND ----------

# MAGIC %sh cat $OUTPUT_DIR/manifest.json

# COMMAND ----------

# MAGIC %md #### List run information

# COMMAND ----------

find_run_dir(output_dir, "RUN_DIR", "manifest.json")

# COMMAND ----------

import glob
files = [f for f in glob.glob(f"{output_dir}/*") if not f.endswith("manifest.json")]
os.environ['RUN_DIR'] = files[0]
files[0]

# COMMAND ----------

# MAGIC %sh ls -lR $RUN_DIR

# COMMAND ----------

# MAGIC %sh  cat $RUN_DIR/run.json