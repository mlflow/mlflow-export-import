# Databricks notebook source
# MAGIC %md ### Copy Model Version
# MAGIC
# MAGIC ##### Overview
# MAGIC
# MAGIC Copy a model version and its run.
# MAGIC
# MAGIC ##### Widgets
# MAGIC
# MAGIC * `1. Src Model` - Source model name.
# MAGIC * `2. Src Version` - Source model version.
# MAGIC * `3. Dst Model` - Destination model name.
# MAGIC * `4. Dst experiment name` - Destination experiment name. 
# MAGIC   * If specified, will copy old version's run to a new run which the new model version will point to.
# MAGIC   * Otherwise, use old version's run for new version.
# MAGIC * `5. Dst URI` - Destination workspace. 
# MAGIC   * Either `databricks` for current workspace, or for different workspace specify secrets scope and prefix per [Set up the API token for a remote registry](https://docs.databricks.com/en/machine-learning/manage-model-lifecycle/multiple-workspaces.html#set-up-the-api-token-for-a-remote-registry). Examples:
# MAGIC     * `databricks` - current workspace
# MAGIC     * `databricks://MY-SCOPE:MY-PREFIX` - other workspace
# MAGIC * `6. Verbose`

# COMMAND ----------

# MAGIC %md #### Setup

# COMMAND ----------

# MAGIC %run ./Common

# COMMAND ----------

dbutils.widgets.text("1. Src Model", "") 
src_model_name = dbutils.widgets.get("1. Src Model")

dbutils.widgets.text("2. Src Version", "") 
src_model_version = dbutils.widgets.get("2. Src Version")

dbutils.widgets.text("3. Dst Model", "") 
dst_model_name = dbutils.widgets.get("3. Dst Model")

dbutils.widgets.text("4. Dst experiment name", "") 
dst_experiment_name = dbutils.widgets.get("4. Dst experiment name")
dst_experiment_name = dst_experiment_name if dst_experiment_name else None

dbutils.widgets.text("5. Dst URI", "databricks") 
dst_mlflow_uri = dbutils.widgets.get("5. Dst URI")

dbutils.widgets.dropdown("6. Verbose", "no", ["yes","no"])
verbose = dbutils.widgets.get("6. Verbose") == "yes"

print("src_model_name:", src_model_name)
print("src_model_version:", src_model_version)
print("dst_model_name:", dst_model_name)
print("dst_experiment_name:", dst_experiment_name)
print("dst_mlflow_uri:", dst_mlflow_uri)
print("verbose:", verbose)

# COMMAND ----------

assert_widget(src_model_name, "1. Src Model")
assert_widget(src_model_version, "2. Src Version")
assert_widget(dst_model_name, "3. Dst Model")
assert_widget(dst_experiment_name, "4. Dst experiment name")
assert_widget(dst_mlflow_uri, "5. Dst URI")

# COMMAND ----------

# MAGIC %md #### Copy model version

# COMMAND ----------

# DBTITLE 0,+
from mlflow_export_import.copy import copy_model_version 

dst_model_version = copy_model_version.copy(
    src_model_name,
    src_model_version,
    dst_model_name,
    dst_experiment_name,
    src_mlflow_uri = "databricks",
    dst_mlflow_uri = dst_mlflow_uri,
    verbose = verbose,
)

# COMMAND ----------

# MAGIC %md #### Dump source model version

# COMMAND ----------

import mlflow
client = mlflow.MlflowClient()
vr = client.get_model_version(src_model_name, src_model_version)
dump_obj(vr, "Source ModelVersion")

# COMMAND ----------

# MAGIC %md #### Dump destination model version

# COMMAND ----------

dump_obj(dst_model_version, "Source ModelVersion")
