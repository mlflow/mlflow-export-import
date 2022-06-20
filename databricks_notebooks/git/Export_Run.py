# Databricks notebook source
# MAGIC %md ### Export Run
# MAGIC 
# MAGIC ##### Overview
# MAGIC * Exports an run and its artifacts to a folder.
# MAGIC * Output file `run.json` contains top-level run metadata.
# MAGIC * Notebooks are also exported in several formats.
# MAGIC 
# MAGIC #### Output folder
# MAGIC ```
# MAGIC 
# MAGIC +-artifacts/
# MAGIC | +-plot.png
# MAGIC | +-sklearn-model/
# MAGIC | | +-model.pkl
# MAGIC | | +-conda.yaml
# MAGIC | |
# MAGIC +-run.json
# MAGIC ```
# MAGIC 
# MAGIC ##### Widgets
# MAGIC * Run ID 
# MAGIC * Destination base folder- Base output folder to which the Run ID will be appended to.
# MAGIC * Export metadata tags - Log source metadata such as:
# MAGIC   * mlflow_export_import.info.experiment_id
# MAGIC   * mlflow_export_import.metadata.experiment-name	
# MAGIC * Notebook formats:
# MAGIC   * Standard Databricks notebook formats such as SOURCE, HTML, JUPYTER, DBC. See [Databricks Export Format](https://docs.databricks.com/dev-tools/api/latest/workspace.html#notebookexportformat)  documentation.
# MAGIC   
# MAGIC #### Setup
# MAGIC * See Setup in [README]($00_README_Export_Import).

# COMMAND ----------

# MAGIC %run ./Common

# COMMAND ----------

# MAGIC %md ### Setup

# COMMAND ----------

dbutils.widgets.text(" Run ID", "") 
run_id = dbutils.widgets.get(" Run ID")

dbutils.widgets.text("Destination base folder", "dbfs:/mnt/andre-work/exim/experiments") 
output_dir = dbutils.widgets.get("Destination base folder")
output_dir += f"/{run_id}"

dbutils.widgets.dropdown("Export source tags","no",["yes","no"])
export_source_tags = dbutils.widgets.get("Export source tags") == "yes"

all_formats = [ "SOURCE", "DBC", "HTML", "JUPYTER" ]
dbutils.widgets.multiselect("Notebook formats",all_formats[0],all_formats)
formats = dbutils.widgets.get("Notebook formats")
formats = formats.split(",")
if "" in formats: formats.remove("")

print("run_id:",run_id)
print("output_dir:",output_dir)
print("export_source_tags:",export_source_tags)
print("formats:",formats)

# COMMAND ----------

if len(run_id)==0: raise Exception("ERROR: Run ID is required")
if len(output_dir)==0: raise Exception("ERROR: DBFS destination is required")
  
import mlflow

# COMMAND ----------

# MAGIC %md ### Display MLflow UI URI of Run

# COMMAND ----------

display_run_uri(run_id)

# COMMAND ----------

# MAGIC %md ### Remove any previous exported run data

# COMMAND ----------

dbutils.fs.rm(output_dir, True)

# COMMAND ----------

# MAGIC %md ### Export the run

# COMMAND ----------

from mlflow_export_import.run.export_run import RunExporter
exporter = RunExporter(mlflow.tracking.MlflowClient(),
                       notebook_formats=formats, 
                       export_source_tags=export_source_tags)
exporter.export_run(run_id, output_dir)

# COMMAND ----------

# MAGIC %md ### Display  exported run files

# COMMAND ----------

import os
output_dir = output_dir.replace("dbfs:","/dbfs")
os.environ['OUTPUT_DIR'] = output_dir

# COMMAND ----------

# MAGIC %sh echo $OUTPUT_DIR

# COMMAND ----------

# MAGIC %sh ls -l $OUTPUT_DIR

# COMMAND ----------

# MAGIC %sh cat $OUTPUT_DIR/run.json

# COMMAND ----------

# MAGIC %sh ls -lR $OUTPUT_DIR/artifacts