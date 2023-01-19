# Databricks notebook source
# MAGIC %md ### Export Experiment
# MAGIC 
# MAGIC #### Overview
# MAGIC * Exports an experiment and its runs (artifacts too) to a DBFS directory.
# MAGIC * Output file `experiment.json` contains top-level experiment metadata.
# MAGIC * Each run and its artifacts are stored as a sub-directory whose name is that of the run_id.
# MAGIC * Notebooks also can be exported in several formats.
# MAGIC 
# MAGIC ##### Output folder
# MAGIC ```
# MAGIC 
# MAGIC +-experiment.json
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
# MAGIC * Experiment ID or name - Either the experiment ID or experiment name.
# MAGIC * Output base directory - Base output folder of the exported experiment. All the experiment data will be saved here under the experiment ID folder.	
# MAGIC * Notebook formats:
# MAGIC   * Standard Databricks notebook formats such as SOURCE, HTML, JUPYTER, DBC. See [Databricks Export Format](https://docs.databricks.com/dev-tools/api/latest/workspace.html#notebookexportformat) documentation.
# MAGIC 
# MAGIC #### Setup
# MAGIC * See Setup in [README]($./_README).

# COMMAND ----------

# MAGIC %md ### Setup

# COMMAND ----------

# MAGIC %run ./Common

# COMMAND ----------

dbutils.widgets.text("1. Experiment ID or Name", "") 
experiment_id_or_name = dbutils.widgets.get("1. Experiment ID or Name")
 
dbutils.widgets.text("2. Output base directory", "") 
output_dir = dbutils.widgets.get("2. Output base directory")

notebook_formats = get_notebook_formats(3)

print("experiment_id_or_name:", experiment_id_or_name)
print("output_dir:", output_dir)
print("notebook_formats:", notebook_formats)

# COMMAND ----------

assert_widget(experiment_id_or_name, "1. Experiment ID or Name")
assert_widget(output_dir, "2. Output base directory")
  
import mlflow
from mlflow_export_import.common import mlflow_utils 

client = mlflow.tracking.MlflowClient()
experiment = mlflow_utils.get_experiment(client, experiment_id_or_name)
output_dir = f"{output_dir}/{experiment.experiment_id}"
print("experiment_id:",experiment.experiment_id)
print("experiment_name:",experiment.name)       
print("output_dir:",output_dir)

# COMMAND ----------

# MAGIC %md ### Display MLflow UI URI of Experiment

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

# %sh ls -l /dbfs/mnt/andre-work/exim/experiments
# 12927081/12927081/b29df707abcc4d21bf7b3d5c182a12a2

# COMMAND ----------

from mlflow_export_import.experiment.export_experiment import ExperimentExporter

exporter = ExperimentExporter(
    client, 
    notebook_formats = notebook_formats)
exporter.export_experiment(
    exp_id_or_name = experiment.experiment_id, 
    output_dir = output_dir)

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