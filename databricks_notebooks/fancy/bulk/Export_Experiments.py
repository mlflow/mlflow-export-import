# Databricks notebook source
# MAGIC %md ## Export Experiments
# MAGIC 
# MAGIC Export multiple experiments and all their runs.
# MAGIC 
# MAGIC Widgets
# MAGIC * `1. Experiments` - comma delimited list of either experiment IDs or experiment names. `all` will export all experiments.
# MAGIC * `2. Output directory` - shared directory between source and destination workspaces.
# MAGIC * `3. Export permissions` - export Databricks permissions.
# MAGIC * `4. Notebook formats`
# MAGIC * `5. Use threads`

# COMMAND ----------

# MAGIC %run ./Common

# COMMAND ----------

dbutils.widgets.text("1. Experiments", "") 
experiments = dbutils.widgets.get("1. Experiments")

dbutils.widgets.text("2. Output directory", "") 
output_dir = dbutils.widgets.get("2. Output directory")
output_dir = output_dir.replace("dbfs:","/dbfs")

dbutils.widgets.dropdown("3. Export permissions","no",["yes","no"])
export_permissions = dbutils.widgets.get("3. Export permissions") == "yes"

all_formats = [ "SOURCE", "DBC", "HTML", "JUPYTER" ]
dbutils.widgets.multiselect("4. Notebook formats",all_formats[0],all_formats)
notebook_formats = dbutils.widgets.get("4. Notebook formats")

dbutils.widgets.dropdown("5. Use threads","False",["True","False"])
use_threads = dbutils.widgets.get("5. Use threads") == "True"

print("experiments:", experiments)
print("output_dir:", output_dir)
print("export_permissions:", export_permissions)
print("notebook_formats:", notebook_formats)
print("use_threads:", use_threads)

# COMMAND ----------

assert_widget(experiments, "1. Experiments")
assert_widget(output_dir, "2. Output directory")

# COMMAND ----------

from mlflow_export_import.bulk.export_experiments import export_experiments

export_experiments(
    experiments = experiments, 
    output_dir = output_dir, 
    export_permissions = export_permissions,
    notebook_formats = notebook_formats, 
    use_threads = use_threads
)

# COMMAND ----------

# MAGIC %md ### Display  exported files

# COMMAND ----------

import os
output_dir = output_dir.replace("dbfs:", "/dbfs")
os.environ['OUTPUT_DIR'] = output_dir
output_dir

# COMMAND ----------

# MAGIC %sh 
# MAGIC echo "OUTPUT_DIR: $OUTPUT_DIR" ; echo
# MAGIC ls $OUTPUT_DIR

# COMMAND ----------

# MAGIC %sh cat $OUTPUT_DIR/experiments.json

# COMMAND ----------

# MAGIC %sh ls -lR $OUTPUT_DIR
