# Databricks notebook source
# MAGIC %md ## Copy Model Version
# MAGIC
# MAGIC #### Overview
# MAGIC
# MAGIC * Copies a model version and its run (deep copy) to a new model version.
# MAGIC * The new model version can be either in the same workspace or in another.
# MAGIC * Supports both standard Workspace registry and the new Unity Catalog (UC) model registry.
# MAGIC * Databricks registry URIs should be Databricks secrets tuples per [Specify a remote registry](https://docs.databricks.com/en/machine-learning/manage-model-lifecycle/multiple-workspaces.html).
# MAGIC   * Example: `registry_uri = f'databricks://<scope>:<prefix>'`
# MAGIC
# MAGIC
# MAGIC #### Widgets
# MAGIC
# MAGIC * `1. Source Model` - Source model name.
# MAGIC * `2. Source Version` - Source model version.
# MAGIC * `3. Destination Model` - Destination model name.
# MAGIC * `4. Destination experiment name` - Destination experiment name. 
# MAGIC   * If specified, copies source version's run to a new run which the new model version points to.
# MAGIC   * If not specified, the new run uses the source version's run.
# MAGIC * `5. Source Run Workspace` - Workspace for the run of the source model version. 
# MAGIC   * If copying from current workspace, then leave blank or set to `databricks`.
# MAGIC   * If copying from another workspace, then specify secrets scope and prefix per [Set up the API token for a remote registry](https://docs.databricks.com/en/machine-learning/manage-model-lifecycle/multiple-workspaces.html#set-up-the-api-token-for-a-remote-registry). 
# MAGIC     * Example: `databricks://MY-SCOPE:MY-PREFIX`.
# MAGIC * `6. Copy lineage tags` - Add source lineage info to destination version as tags starting with 'mlflow_exim'.
# MAGIC * `7. Verbose`
# MAGIC * `8. Return result` for automated testing.

# COMMAND ----------

# MAGIC %md ### Diagrams
# MAGIC
# MAGIC In the two diagram below, the left shallow copy is **_bad_**, and the right deep copy is **_good_**.

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

dbutils.widgets.text("5. Source Run Workspace", "databricks") 
src_run_workspace = dbutils.widgets.get("5. Source Run Workspace")
src_run_workspace = src_run_workspace or "databricks"

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
print("src_run_workspace:", src_run_workspace)
print("copy_lineage_tags:", copy_lineage_tags)
print("verbose:", verbose)
print("return_result:", return_result)

# COMMAND ----------

assert_widget(src_model_name, "1. Source Model")
assert_widget(src_model_version, "2. Source Version")
assert_widget(dst_model_name, "3. Destination Model")
assert_widget(dst_experiment_name, "4. Destination experiment name")
assert_widget(src_run_workspace, "5. Run Workspace")

# COMMAND ----------

# MAGIC %md #### Copy Model Version

# COMMAND ----------

src_model_version, dst_model_version = copy_model_version(
    src_model_name,
    src_model_version,
    dst_model_name,
    dst_experiment_name,
    src_run_workspace = src_run_workspace,
    copy_lineage_tags = copy_lineage_tags,
    verbose = verbose
)

# COMMAND ----------

# MAGIC %md #### Display Source Model Version

# COMMAND ----------

display_registered_model_version_uri(src_model_version.name, src_model_version.version)

# COMMAND ----------

dump_obj_as_json(src_model_version, "Source ModelVersion")

# COMMAND ----------

# MAGIC %md #### Display Destination Model Version

# COMMAND ----------

display_registered_model_version_uri(dst_model_version.name, dst_model_version.version)

# COMMAND ----------

dump_obj_as_json(dst_model_version, "Destination ModelVersion")

# COMMAND ----------

# MAGIC %md #### Return value

# COMMAND ----------

if return_result:
  result = {
      "src_model_version": obj_to_dict(src_model_version),
      "dst_model_version": obj_to_dict(dst_model_version)
  }
  dbutils.notebook.exit(dict_to_json(result))