# Databricks notebook source
# MAGIC %md ## Export Experiments
# MAGIC
# MAGIC Export multiple experiments and all their runs.
# MAGIC
# MAGIC Widgets
# MAGIC * `1. Experiments` - comma delimited list of either experiment IDs or experiment names. `all` will export all experiments.
# MAGIC * `2. Output directory` - shared directory between source and destination workspaces.
# MAGIC * `3. Run start date` - Export runs after this UTC date (inclusive). Example: `2023-04-05`.
# MAGIC * `4. Export permissions` - export Databricks permissions.
# MAGIC * `5. Export deleted runs`
# MAGIC * `6. Notebook formats`
# MAGIC * `7. Use threads`

# COMMAND ----------

# MAGIC %run ./Common

# COMMAND ----------

dbutils.widgets.text("1. Experiments", "") 
experiments = dbutils.widgets.get("1. Experiments")

dbutils.widgets.text("2. Output directory", "") 
output_dir = dbutils.widgets.get("2. Output directory")
output_dir = output_dir.replace("dbfs:","/dbfs")

dbutils.widgets.text("3. Run start date", "") 
run_start_date = dbutils.widgets.get("3. Run start date")

dbutils.widgets.dropdown("4. Export permissions","no",["yes","no"])
export_permissions = dbutils.widgets.get("4. Export permissions") == "yes"

dbutils.widgets.dropdown("5. Export deleted runs","no",["yes","no"])
export_deleted_runs = dbutils.widgets.get("5. Export deleted runs") == "yes"

all_formats = [ "SOURCE", "DBC", "HTML", "JUPYTER" ]
dbutils.widgets.multiselect("6. Notebook formats",all_formats[0],all_formats)
notebook_formats = dbutils.widgets.get("6. Notebook formats")

dbutils.widgets.dropdown("7. Use threads","False",["True","False"])
use_threads = dbutils.widgets.get("7. Use threads") == "True"

if run_start_date=="": run_start_date = None

print("experiments:", experiments)
print("output_dir:", output_dir)
print("run_start_date:", run_start_date)
print("export_permissions:", export_permissions)
print("export_deleted_runs:", export_deleted_runs)
print("notebook_formats:", notebook_formats)
print("use_threads:", use_threads)

# COMMAND ----------

# DBTITLE 1,set up log file
import os 
from datetime import datetime
import pytz

cst = pytz.timezone('US/Central')
now = datetime.now(tz=cst)
date = now.strftime("%Y-%m-%d-%H:%M:%S")
 
logfile = f"export_experiments.{date}.log"
os.environ["MLFLOW_EXPORT_IMPORT_LOG_OUTPUT_FILE"] = logfile 

print("Logging to", logfile)

# COMMAND ----------

assert_widget(experiments, "1. Experiments")
assert_widget(output_dir, "2. Output directory")

# COMMAND ----------

from mlflow_export_import.bulk.export_experiments import export_experiments

export_experiments(
    experiments = experiments, 
    output_dir = output_dir, 
    run_start_time = run_start_date,
    export_permissions = export_permissions,
    export_deleted_runs = export_deleted_runs,
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
