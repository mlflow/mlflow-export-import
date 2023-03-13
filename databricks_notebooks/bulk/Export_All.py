# Databricks notebook source
# MAGIC %md ## Export All
# MAGIC 
# MAGIC Export all the MLflow registered models and all experiments of a tracking server.
# MAGIC 
# MAGIC **Widgets**
# MAGIC * `1. Output directory`
# MAGIC * `2. Stages` - comma seperated stages to be exported
# MAGIC * `3. Use threads`
# MAGIC * Export all runs - TODO
# MAGIC * Notebook formats - TODO

# COMMAND ----------

# MAGIC %run ./Common

# COMMAND ----------

dbutils.widgets.text("1. Output directory", "") 
output_dir = dbutils.widgets.get("1. Output directory")
output_dir = output_dir.replace("dbfs:","/dbfs")
 
all_formats = [ "SOURCE", "DBC", "HTML", "JUPYTER" ]
dbutils.widgets.multiselect("2. Notebook formats",all_formats[0],all_formats)
notebook_formats = dbutils.widgets.get("2. Notebook formats")

dbutils.widgets.dropdown("3. Use threads","no",["yes","no"])
use_threads = dbutils.widgets.get("3. Use threads") == "yes"
 
print("output_dir:",output_dir)
print("notebook_formats:",notebook_formats)
print("use_threads:",use_threads)

# COMMAND ----------

assert_widget(output_dir, "1. Output directory")

# COMMAND ----------

from mlflow_export_import.bulk.export_all import export_all

export_all(
    output_dir = output_dir, 
    notebook_formats = notebook_formats, 
    use_threads = use_threads
)