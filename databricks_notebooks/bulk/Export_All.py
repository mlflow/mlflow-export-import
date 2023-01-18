# Databricks notebook source
# MAGIC %md ## Export All
# MAGIC * Export all the MLflow registered models and all experiments of a tracking server.

# COMMAND ----------

# MAGIC %sh pip install mlflow-export-import

# COMMAND ----------

dbutils.widgets.text("1. Output directory", "") 
output_dir = dbutils.widgets.get("1. Output directory")
output_dir = output_dir.replace("dbfs:","/dbfs")
 
all_formats = [ "SOURCE", "DBC", "HTML", "JUPYTER" ]
dbutils.widgets.multiselect("2. Notebook formats",all_formats[0],all_formats)
notebook_formats = dbutils.widgets.get("2. Notebook formats")

dbutils.widgets.dropdown("3. Use threads","no",["yes","no"])
use_threads = dbutils.widgets.get("3. Use threads") == "yes"
 
if output_dir=="":
    raise Exception("Missing widget '1. Output base directory'")
 
print("output_dir:",output_dir)
print("notebook_formats:",notebook_formats)
print("use_threads:",use_threads)

# COMMAND ----------

import mlflow
from mlflow_export_import.bulk.export_all import export_all

# COMMAND ----------

export_all(output_dir=output_dir, 
           notebook_formats=notebook_formats, 
           use_threads=use_threads)