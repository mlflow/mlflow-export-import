# Databricks notebook source
# MAGIC %md ### Export Run
# MAGIC 
# MAGIC ##### Overview
# MAGIC * Exports a run and its artifacts to a folder.
# MAGIC * Output file `run.json` contains run metadata to be able to rehydrate the run.
# MAGIC * Notebooks are also exported in several formats.
# MAGIC 
# MAGIC #### Output folder
# MAGIC ```
# MAGIC +-artifacts/
# MAGIC | +-sklearn-model/
# MAGIC | | +-model.pkl
# MAGIC | | +-conda.yaml
# MAGIC | |
# MAGIC +-run.json
# MAGIC ```
# MAGIC 
# MAGIC ##### Widgets
# MAGIC * `1. Run ID` 
# MAGIC * `2. Output base directory` - Base output directory of the exported run.
# MAGIC * `3. Notebook formats` - Standard Databricks notebook formats such as SOURCE, HTML, JUPYTER, DBC. 

# COMMAND ----------

# MAGIC %run ./Common

# COMMAND ----------

# MAGIC %md ### Setup

# COMMAND ----------

dbutils.widgets.text("1. Run ID", "") 
run_id = dbutils.widgets.get("1. Run ID")

dbutils.widgets.text("2. Output base directory", "") 
output_dir = dbutils.widgets.get("2. Output base directory")
output_dir += f"/{run_id}"

notebook_formats = get_notebook_formats(3)

print("run_id:", run_id)
print("output_dir:", output_dir)
print("notebook_formats:", notebook_formats)

# COMMAND ----------

assert_widget(run_id, "1. Run ID")
assert_widget(output_dir, "2. Output base directory")

# COMMAND ----------

# MAGIC %md ### Display run UI link

# COMMAND ----------

display_run_uri(run_id)

# COMMAND ----------

# MAGIC %md ### Export the run

# COMMAND ----------

from mlflow_export_import.run.export_run import export_run

export_run(
    run_id = run_id, 
    output_dir = output_dir,
    notebook_formats = notebook_formats
)

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
