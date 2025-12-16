# Databricks notebook source
# MAGIC %md ## Export Experiments
# MAGIC
# MAGIC Export multiple experiments and all their runs.
# MAGIC
# MAGIC Widgets
# MAGIC * `1. Experiments` - comma delimited list of either experiment IDs or experiment names. `all` will export all experiments. Or filename (ending with .txt) with experiment names/IDs.
# MAGIC * `2. Output directory` - shared directory between source and destination workspaces.
# MAGIC * `3. Run start date` - Export runs after this UTC date (inclusive). Format: YYYY-MM-DD or YYYY-MM-DD HH:MM:SS. Example: `2023-04-05` or `2023-04-05 08:00:00`.
# MAGIC * `4. Until date` - Export runs before this UTC date (exclusive). Use with Run start date to define a time window. Format: YYYY-MM-DD or YYYY-MM-DD HH:MM:SS. Example: `2023-05-01` or `2023-04-05 12:00:00`.
# MAGIC * `5. Export permissions` - export Databricks permissions.
# MAGIC * `6. Export deleted runs`
# MAGIC * `7. Notebook formats`
# MAGIC * `8. Use threads`

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

dbutils.widgets.text("4. Until date", "") 
until_date = dbutils.widgets.get("4. Until date")

dbutils.widgets.dropdown("5. Export permissions","no",["yes","no"])
export_permissions = dbutils.widgets.get("5. Export permissions") == "yes"

dbutils.widgets.dropdown("6. Export deleted runs","no",["yes","no"])
export_deleted_runs = dbutils.widgets.get("6. Export deleted runs") == "yes"

notebook_formats = get_notebook_formats(7)

dbutils.widgets.dropdown("8. Use threads","False",["True","False"])
use_threads = dbutils.widgets.get("8. Use threads") == "True"

if run_start_date=="": run_start_date = None
if until_date=="": until_date = None

print("experiments:", experiments)
print("output_dir:", output_dir)
print("run_start_date:", run_start_date)
print("until_date:", until_date)
print("export_permissions:", export_permissions)
print("export_deleted_runs:", export_deleted_runs)
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
    run_start_time = run_start_date,
    until = until_date,
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
