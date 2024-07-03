# Databricks notebook source
# MAGIC %md ## Copy Run
# MAGIC
# MAGIC ##### Overview
# MAGIC
# MAGIC Copy an MLflow run to either the current or to another workspace.
# MAGIC
# MAGIC ##### Widgets
# MAGIC
# MAGIC * `1. Source run ID` - Source run ID.
# MAGIC * `2. Destination experiment name` - Destination experiment name of the run.
# MAGIC * `3. Destination workspace` - Destination workspace - default is current workspace.

# COMMAND ----------

# MAGIC %md #### Setup

# COMMAND ----------

# MAGIC %run ./Common

# COMMAND ----------

dbutils.widgets.text("1. Source run ID", "") 
src_run_id = dbutils.widgets.get("1. Source run ID")

dbutils.widgets.text("2. Destination experiment", "") 
dst_experiment_name = dbutils.widgets.get("2. Destination experiment")

dbutils.widgets.text("3. Destination workspace", "databricks") 
dst_run_workspace = dbutils.widgets.get("3. Destination workspace")
dst_run_workspace = dst_run_workspace or "databricks"

print("src_run_id:", src_run_id)
print("dst_experiment_name:", dst_experiment_name)
print("dst_run_workspace:", dst_run_workspace)

# COMMAND ----------

assert_widget(src_run_id, "1. Source run ID")
assert_widget(dst_experiment_name, "2. Destination experiment name")

# COMMAND ----------

# MAGIC %md #### Copy Run

# COMMAND ----------

from mlflow_export_import.copy.copy_run import copy

dst_run = copy(src_run_id, dst_experiment_name, "databricks", dst_run_workspace)

# COMMAND ----------

dst_run

# COMMAND ----------

if dst_run_workspace == "databricks":
    display_run_uri(dst_run.info.run_id)
else:
    print(f"Cannot display run '{dst_run.info.run_id}' since it is in a remove workspace.")
