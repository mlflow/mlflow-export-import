# Databricks notebook source
# MAGIC %md ## Copy Model Version
# MAGIC
# MAGIC ##### Overview
# MAGIC
# MAGIC Copy a model version and its run to a new model version. 
# MAGIC
# MAGIC The source version's run can also be copied if you specifiy a destination experiment.
# MAGIC
# MAGIC ##### Widgets
# MAGIC
# MAGIC * `1. Source Model` - Source model name.
# MAGIC * `2. Source Version` - Source model version.
# MAGIC * `3. Destination Model` - Destination model name.
# MAGIC * `4. Destination experiment name` - Destination experiment name. 
# MAGIC   * If specified, will copy old version's run to a new run which the new model version will point to.
# MAGIC   * If not specified, use old version's run for new version.
# MAGIC * `5. Destination Workspace` - Destination workspace. `databricks` for current workspace or for different workspace specify secrets scope and prefix per [Set up the API token for a remote registry](https://docs.databricks.com/en/machine-learning/manage-model-lifecycle/multiple-workspaces.html#set-up-the-api-token-for-a-remote-registry). Examples:
# MAGIC     * `databricks` - current workspace
# MAGIC     * `databricks://MY-SCOPE:MY-PREFIX` - other workspace
# MAGIC * `6. Verbose`

# COMMAND ----------

# MAGIC %md #### Setup

# COMMAND ----------

# MAGIC %run ./Common

# COMMAND ----------

dbutils.widgets.text("1. Source Model", "") 
src_model_name = dbutils.widgets.get("1. Source Model")

dbutils.widgets.text("2. Source Version", "") 
src_model_version = dbutils.widgets.get("2. Source Version")

dbutils.widgets.text("3. Destination Model", "") 
dst_model_name = dbutils.widgets.get("3. Destination Model")

dbutils.widgets.text("4. Destination experiment name", "") 
dst_experiment_name = dbutils.widgets.get("4. Destination experiment name")
dst_experiment_name = dst_experiment_name if dst_experiment_name else None

dbutils.widgets.text("5. Destination Workspace", "databricks") 
dst_tracking_uri = dbutils.widgets.get("5. Destination Workspace")

dbutils.widgets.dropdown("6. Verbose", "yes", ["yes","no"])
verbose = dbutils.widgets.get("6. Verbose") == "yes"

print("src_model_name:", src_model_name)
print("src_model_version:", src_model_version)
print("dst_model_name:", dst_model_name)
print("dst_experiment_name:", dst_experiment_name)
print("dst_tracking_uri:", dst_tracking_uri)
print("verbose:", verbose)

# COMMAND ----------

assert_widget(src_model_name, "1. Source Model")
assert_widget(src_model_version, "2. Source Version")
assert_widget(dst_model_name, "3. Destination Model")
assert_widget(dst_experiment_name, "4. Destination experiment name")
assert_widget(dst_tracking_uri, "5. Destination Workspace")

# COMMAND ----------

# MAGIC %md #### Copy model version

# COMMAND ----------

src_model_version, dst_model_version = copy_model_version(
    src_model_name,
    src_model_version,
    dst_model_name,
    dst_experiment_name,
    dst_tracking_uri = dst_tracking_uri,
    verbose = verbose
)

# COMMAND ----------

# MAGIC %md #### Show source model version

# COMMAND ----------

display_registered_model_version_uri(src_model_version.name, src_model_version.version)

# COMMAND ----------

dump_obj_as_json(src_model_version, "Source ModelVersion")

# COMMAND ----------

# MAGIC %md #### Show destination model version

# COMMAND ----------

display_registered_model_version_uri(dst_model_version.name, dst_model_version.version)

# COMMAND ----------

dump_obj_as_json(dst_model_version, "Destination ModelVersion")
