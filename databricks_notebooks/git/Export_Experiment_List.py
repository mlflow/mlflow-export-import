# Databricks notebook source
# MAGIC %md ### Export Experiment List - WIP
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

# MAGIC %run ./Common

# COMMAND ----------

dbutils.widgets.text(" Experiments", "") 
experiments = dbutils.widgets.get(" Experiments")
 
dbutils.widgets.text("Destination base folder", "dbfs:/mnt/andre-work/exim/experiments/experiments_list") 
output_dir = dbutils.widgets.get("Destination base folder")

dbutils.widgets.dropdown("Export metadata tags","no",["yes","no"])
export_metadata_tags = dbutils.widgets.get("Export metadata tags") == "yes"

all_formats = [ "SOURCE", "DBC", "HTML", "JUPYTER" ]
dbutils.widgets.multiselect("Notebook formats",all_formats[0],all_formats)
formats = dbutils.widgets.get("Notebook formats")

experiments, output_dir, export_metadata_tags, formats

# COMMAND ----------

if len(experiments)==0: raise Exception("ERROR: Experiments are required")
if len(output_dir)==0: raise Exception("ERROR: DBFS destination is required")
  
import mlflow
from mlflow_export_import.common import mlflow_utils 

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

from mlflow_export_import.experiment.export_experiment_list import export_experiment_list
export_experiment_list(experiments, output_dir, export_metadata_tags, formats)

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

# MAGIC %sh ls -l $OUTPUT_DIR

# COMMAND ----------

# MAGIC %sh ls -lR $OUTPUT_DIR