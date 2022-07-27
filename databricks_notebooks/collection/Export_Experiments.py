# Databricks notebook source
# MAGIC %md ## Export Experiments
# MAGIC 
# MAGIC Widgets
# MAGIC * Experiments - comma delimited - either experiment ID or experiment name
# MAGIC * Based output directory
# MAGIC * Export source tags
# MAGIC * Notebook formats
# MAGIC * Use threads
# MAGIC 
# MAGIC See https://github.com/mlflow/mlflow-export-import/blob/master/README_bulk.md#experiments.

# COMMAND ----------

# MAGIC %sh pip install mlflow-export-import

# COMMAND ----------

dbutils.widgets.text("1. Experiments", "") 
experiments = dbutils.widgets.get("1. Experiments")

dbutils.widgets.text("2. Output base directory", "dbfs:/mnt/andre-work/exim/experiments") 
output_dir = dbutils.widgets.get("2. Output base directory")
output_dir = output_dir.replace("dbfs:","/dbfs")

dbutils.widgets.dropdown("3. Export source tags","no",["yes","no"])
export_source_tags = dbutils.widgets.get("3. Export source tags") == "yes"

all_formats = [ "SOURCE", "DBC", "HTML", "JUPYTER" ]
dbutils.widgets.multiselect("4. Notebook formats",all_formats[0],all_formats)
notebook_formats = dbutils.widgets.get("4. Notebook formats")

dbutils.widgets.dropdown("5. Use threads","no",["yes","no"])
use_threads = dbutils.widgets.get("5. Use threads") == "yes"

print("experiments:",experiments)
print("output_dir:",output_dir)
print("export_source_tags:",export_source_tags)
print("notebook_formats:",notebook_formats)
print("use_threads:",use_threads)

# COMMAND ----------

if len(experiments)==0: raise Exception("ERROR: Experiments are required")
if len(output_dir)==0: raise Exception("ERROR: Output base directory is required")

# COMMAND ----------

import mlflow
from mlflow_export_import.bulk.export_experiments import export_experiments
export_experiments(mlflow.tracking.MlflowClient(), experiments, output_dir, export_source_tags, notebook_formats, use_threads)

# COMMAND ----------

# MAGIC %md ### Display  exported files

# COMMAND ----------

import os
output_dir = output_dir.replace("dbfs:","/dbfs")
os.environ['OUTPUT_DIR'] = output_dir
output_dir

# COMMAND ----------

# MAGIC %sh echo $OUTPUT_DIR

# COMMAND ----------

# MAGIC %sh cat $OUTPUT_DIR/manifest.json

# COMMAND ----------

# MAGIC %sh ls -lR $OUTPUT_DIR