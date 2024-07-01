# Databricks notebook source
# MAGIC %md ## Copy Model Version
# MAGIC
# MAGIC ##### Overview
# MAGIC
# MAGIC * Copies a model version and its run (deep copy) to a new model version.
# MAGIC * Supports both the Unity Catalog (UC) and classical Workspace (WS) model registry.
# MAGIC * The new model version's run can be either in the current workspace or in another workspace.
# MAGIC * Can be used to migrate non-UC model versions to UC model versions provided the source model version has a signature.
# MAGIC * Databricks registry URIs should be based on three Databricks secrets with a common prefix per [Specify a remote registry](https://docs.databricks.com/en/machine-learning/manage-model-lifecycle/multiple-workspaces.html#specify-a-remote-registry).
# MAGIC   * Example: `registry_uri = 'databricks://<scope>:<prefix>'`
# MAGIC * For more documentation see: https://github.com/mlflow/mlflow-export-import/blob/master/README_copy.md#copy-model-version.
# MAGIC
# MAGIC ##### Usage
# MAGIC   * Copies WS model version to a WS model version.
# MAGIC   * Copies WS model version to a UC model version (provided the WS MLflow model has a signature)
# MAGIC   * Copies UC model version to a UC model version.
# MAGIC   * Copies UC model version to a WS model version.
# MAGIC
# MAGIC ##### Widgets
# MAGIC
# MAGIC * `1. Source Model` - Source model name.
# MAGIC * `2. Source Version` - Source model version.
# MAGIC * `3. Destination Model` - Destination model name.
# MAGIC * `4. Destination experiment name` - Destination experiment name (workspace path). 
# MAGIC   * If specified, copies source version's run to a new run which the new model version points to.
# MAGIC   * If not specified, the new run uses the source version's run (shallow copy).
# MAGIC   * Both source and destination workspaces must share the same UC metastore.
# MAGIC * `5. Destination Workspace` - Workspace for the destination model version (if a workspace model) and its run. 
# MAGIC   * Default is "databricks" which is the current workspace.
# MAGIC   * If copying to another workspace, then specify secrets scope and prefix per [Set up the API token for a remote registry](https://docs.databricks.com/en/machine-learning/manage-model-lifecycle/multiple-workspaces.html#set-up-the-api-token-for-a-remote-registry). 
# MAGIC     * Example: `databricks://MY-SCOPE:MY-PREFIX`.
# MAGIC * `6. Copy lineage tags` - Add source lineage info to destination version as tags starting with 'mlflow_exim'.
# MAGIC * `7. Verbose` - show more details.
# MAGIC * `8. Return result` - Only for automated testing with [Test_Copy_Model_Version]($tests/Test_Copy_Model_Version).
# MAGIC
# MAGIC ##### Documentation
# MAGIC * [Promote a model across environments](https://docs.databricks.com/en/machine-learning/manage-model-lifecycle/index.html#promote-a-model-across-environments)
# MAGIC * [Specify a remote registry](https://docs.databricks.com/en/machine-learning/manage-model-lifecycle/multiple-workspaces.html#specify-a-remote-registry)
# MAGIC
# MAGIC ##### Github
# MAGIC * https://github.com/mlflow/mlflow-export-import/blob/master/databricks_notebooks/copy/Copy_Model_Version.py

# COMMAND ----------

# MAGIC %md ### Diagrams
# MAGIC
# MAGIC In the two diagrams below, the left shallow copy is **_not so good_**, while the right deep copy is **_good_**.

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC ### Unity Catalog Model Registry
# MAGIC
# MAGIC  <img src="https://github.com/mlflow/mlflow-export-import/blob/issue-138-copy-model-version/diagrams/Copy_Model_Version_UC.png?raw=true"  width="700" />

# COMMAND ----------

# MAGIC  %md ### Workspace Model Registry
# MAGIC
# MAGIC  <img src="https://github.com/mlflow/mlflow-export-import/blob/issue-138-copy-model-version/diagrams/Copy_Model_Version_NonUC.png?raw=true"  width="700" />
# MAGIC

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
dst_workspace = dbutils.widgets.get("5. Destination Workspace")
dst_workspace = dst_workspace or "databricks"

dbutils.widgets.dropdown("6. Copy lineage tags", "no", ["yes","no"])
copy_lineage_tags = dbutils.widgets.get("6. Copy lineage tags") == "yes"

dbutils.widgets.dropdown("7. Verbose", "yes", ["yes","no"])
verbose = dbutils.widgets.get("7. Verbose") == "yes"

dbutils.widgets.dropdown("8. Return result", "no", ["yes","no"])
return_result = dbutils.widgets.get("8. Return result") == "yes"

print("src_model_name:", src_model_name)
print("src_model_version:", src_model_version)
print("dst_model_name:", dst_model_name)
print("dst_experiment_name:", dst_experiment_name)
print("dst_workspace:", dst_workspace)
print("copy_lineage_tags:", copy_lineage_tags)
print("verbose:", verbose)
print("return_result:", return_result)

# COMMAND ----------

assert_widget(src_model_name, "1. Source Model")
assert_widget(src_model_version, "2. Source Version")
assert_widget(dst_model_name, "3. Destination Model")
assert_widget(dst_experiment_name, "4. Destination experiment name")
assert_widget(dst_workspace, "5. Destination Run Workspace")

# COMMAND ----------

# MAGIC %md #### Copy Model Version

# COMMAND ----------

src_model_version, dst_model_version = copy_model_version(
    src_model_name,
    src_model_version,
    dst_model_name,
    dst_experiment_name,
    dst_workspace = dst_workspace,
    copy_lineage_tags = copy_lineage_tags, 
    verbose = verbose
) 

# COMMAND ----------

# MAGIC %md #### Display Source Model Version

# COMMAND ----------

display_registered_model_version_uri(src_model_version.name, src_model_version.version)

# COMMAND ----------

dump_obj_as_json(src_model_version, "Source Model Version")

# COMMAND ----------

# MAGIC %md #### Display Destination Model Version

# COMMAND ----------

display_registered_model_version_uri(dst_model_version.name, dst_model_version.version)

# COMMAND ----------

dump_obj_as_json(dst_model_version, "Destination Model Version")

# COMMAND ----------

# MAGIC %md #### Return value (for testing)

# COMMAND ----------

if return_result: 
  result = {
      "src_model_version": obj_to_dict(src_model_version),
      "dst_model_version": obj_to_dict(dst_model_version)
  }
  dbutils.notebook.exit(dict_to_json(result))
