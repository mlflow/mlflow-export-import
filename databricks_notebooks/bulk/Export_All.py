# Databricks notebook source
# MAGIC %md ## Export All
# MAGIC
# MAGIC Export all the MLflow registered models and all experiments of a tracking server.
# MAGIC
# MAGIC **Widgets**
# MAGIC * `1. Output directory` - shared directory between source and destination workspaces.
# MAGIC * `2. Stages` - comma seperated stages to be exported.
# MAGIC * `3. Export latest versions` - export all or just the "latest" versions.
# MAGIC * `4. Run start date` - Export runs after this UTC date (inclusive). Example: `2023-04-05`.
# MAGIC * `5. Export permissions` - export Databricks permissions.
# MAGIC * `6. Export deleted runs`
# MAGIC * `7. Export version MLflow model`
# MAGIC * `8. Notebook formats`
# MAGIC * `9. Use threads`

# COMMAND ----------

# MAGIC %run ./Common

# COMMAND ----------

dbutils.widgets.text("1. Output directory", "") 
output_dir = dbutils.widgets.get("1. Output directory")
output_dir = output_dir.replace("dbfs:","/dbfs")

dbutils.widgets.multiselect("2. Stages", "Production", ["Production","Staging","Archived","None"])
stages = dbutils.widgets.get("2. Stages")

dbutils.widgets.dropdown("3. Export latest versions","no",["yes","no"])
export_latest_versions = dbutils.widgets.get("3. Export latest versions") == "yes"

dbutils.widgets.text("4. Run start date", "") 
run_start_date = dbutils.widgets.get("4. Run start date")

dbutils.widgets.dropdown("5. Export permissions","no",["yes","no"])
export_permissions = dbutils.widgets.get("5. Export permissions") == "yes"

dbutils.widgets.dropdown("6. Export deleted runs","no",["yes","no"])
export_deleted_runs = dbutils.widgets.get("6. Export deleted runs") == "yes"

dbutils.widgets.dropdown("7. Export version MLflow model","no",["yes","no"]) # TODO
export_version_model = dbutils.widgets.get("7. Export version MLflow model") == "yes"

notebook_formats = get_notebook_formats(8)

dbutils.widgets.dropdown("9. Use threads","no",["yes","no"])
use_threads = dbutils.widgets.get("9. Use threads") == "yes"
 
if run_start_date=="": run_start_date = None

print("output_dir:", output_dir)
print("stages:", stages)
print("export_latest_versions:", export_latest_versions)
print("run_start_date:", run_start_date)
print("export_permissions:", export_permissions)
print("export_deleted_runs:", export_deleted_runs)
print("export_version_model:", export_version_model)
print("notebook_formats:", notebook_formats)
print("use_threads:", use_threads)

# COMMAND ----------

assert_widget(output_dir, "1. Output directory")

# COMMAND ----------

from mlflow_export_import.bulk.export_all import export_all

export_all(
    output_dir = output_dir, 
    stages = stages,
    export_latest_versions = export_latest_versions,
    run_start_time = run_start_date,
    export_permissions = export_permissions,
    export_deleted_runs = export_deleted_runs,
    export_version_model = export_version_model,
    notebook_formats = notebook_formats, 
    use_threads = use_threads
)
