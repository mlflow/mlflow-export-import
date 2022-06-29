# Databricks notebook source
# MAGIC %md ### Export Experiment
# MAGIC 
# MAGIC #### Overview
# MAGIC * Exports an experiment and its runs (artifacts too) to a DBFS directory.
# MAGIC * Output file `manifest.json` contains top-level experiment metadata.
# MAGIC * Each run and its artifacts are stored as a sub-directory whose name is that of the run_id.
# MAGIC * Notebooks also can be exported in several formats.
# MAGIC 
# MAGIC ##### Output folder
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
# MAGIC * Experiment ID or name - Either the experiment ID or experiment name.
# MAGIC * Output base directory - Base output folder of the exported experiment. All the experiment data will be saved here under the experiment ID folder.
# MAGIC * Export source tags - Export source tags such as:
# MAGIC   * mlflow_export_import.info.experiment_id
# MAGIC   * mlflow_export_import.metadata.experiment-name	
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

dbutils.widgets.dropdown("3. Export source tags","no",["yes","no"])
export_source_tags = dbutils.widgets.get("3. Export source tags") == "yes"

notebook_formats = get_notebook_formats(4)

print("experiment_id_or_name:", experiment_id_or_name)
print("output_dir:", output_dir)
print("export_source_tags:", export_source_tags)
print("notebook_formats:", notebook_formats)

# COMMAND ----------

if len(experiment_id_or_name)==0: raise Exception("ERROR: Experiment ID or Name is required")
if len(output_dir)==0: raise Exception("ERROR: DBFS destination base folder is required")
  
import mlflow
from mlflow_export_import.common import mlflow_utils 

client = mlflow.tracking.MlflowClient()
experiment = mlflow_utils.get_experiment(client, experiment_id_or_name)
output_dir = f"{output_dir}/{experiment.experiment_id}"
experiment.experiment_id, experiment.name, output_dir

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

from mlflow_export_import.experiment.export_experiment import ExperimentExporter

exporter = ExperimentExporter(client, export_source_tags, notebook_formats)
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