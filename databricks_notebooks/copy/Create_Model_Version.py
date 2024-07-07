# Databricks notebook source
# MAGIC %md ### Create a Model Version from different sources
# MAGIC
# MAGIC #### Overview
# MAGIC * Creates a model version from an MLflow model URI in the current or in another model registry.
# MAGIC * Works either for a Unity Catalog model registry or Workspace model registry. 
# MAGIC * Will create the target registered model if it doesn't exist.
# MAGIC * If source URI is a 'models:' URI, will copy the source model version's description and tags.
# MAGIC
# MAGIC #### Widgets
# MAGIC
# MAGIC ###### `1. Source Model URI`
# MAGIC
# MAGIC Source URIs that point to an MLflow model. Required. 
# MAGIC
# MAGIC Examples:
# MAGIC   * Registry: `models:/my_catalog.my_schema.my_model/13` 
# MAGIC   * Run: `runs:/319a3eec9fb444d4a70996091b31a940/model` 
# MAGIC   * Volume: `/Volumes/andre_catalog/volumes/mlflow_export_import/single/sklearn_wine_best/run/artifacts/model`
# MAGIC   * DBFS: `/dbfs/home/andre@databricks.com/mlflow_export_import/single/sklearn_wine_best/model`
# MAGIC   * Local (driver disk): `/root/sklearn_wine_best`
# MAGIC   * Cloud s3: `s3:/my-bucket/mlflow-models/sklearn-wine_best`
# MAGIC     * You will need to set up your cloud credentials, i.e. IAM role or `AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY` environment variables.
# MAGIC
# MAGIC ###### `2. Destination Model`
# MAGIC
# MAGIC Destination model name. Required.
# MAGIC
# MAGIC Example: `my_catalog.my_schema.my_model`
# MAGIC
# MAGIC ###### `3. Destination Registry URI`
# MAGIC
# MAGIC Destination registry URI. 
# MAGIC
# MAGIC Default is `databricks-uc` which is the current Unity Catalog model registry. Use `databricks` for a Workspace model registry.
# MAGIC
# MAGIC If creating the model version in another model registry, then create the registry URI with a secrets scope and prefix per [Set up the API token for a remote registry](https://docs.databricks.com/en/machine-learning/manage-model-lifecycle/multiple-workspaces.html#set-up-the-api-token-for-a-remote-registry). 
# MAGIC
# MAGIC Example: `databricks://my_scope:my_prefix` where the three secrets keys with the `my_prefix` prefix are:
# MAGIC   * `my_prefix-host` - `https://raincloud-demo.mycompany.com`
# MAGIC   * `my_prefix-token` - `MY_TOKEN`
# MAGIC   * `my_prefix-workspace-id` - `18121492186110540`
# MAGIC
# MAGIC ###### `4. Description`
# MAGIC
# MAGIC Description for destination model version.
# MAGIC
# MAGIC ###### `5. Destination Alias`
# MAGIC
# MAGIC Alias for destination model version.
# MAGIC
# MAGIC #### Documentation
# MAGIC
# MAGIC * [MlflowClient.create_model_version()](https://mlflow.org/docs/latest/python_api/mlflow.client.html#mlflow.client.MlflowClient.create_model_version) - MLflow documentation
# MAGIC * [Set up the API token for a remote registry](https://docs.databricks.com/en/machine-learning/manage-model-lifecycle/multiple-workspaces.html#set-up-the-api-token-for-a-remote-registry) - Databricks documentation

# COMMAND ----------

# MAGIC %md ##### Setup

# COMMAND ----------

# MAGIC %pip install -Uq mlflow-skinny
# MAGIC dbutils.library.restartPython()

# COMMAND ----------

import mlflow
print("mlflow.version:", mlflow.__version__)
print("mlflow.get_registry_uri:", mlflow.get_registry_uri())

# COMMAND ----------

dbutils.widgets.text("1. Source Model URI", "") 
src_model_uri = dbutils.widgets.get("1. Source Model URI")

dbutils.widgets.text("2. Destination Model", "") 
dst_model_name = dbutils.widgets.get("2. Destination Model")

dbutils.widgets.text("3. Destination Registry URI", "databricks-uc") 
dst_registry_uri = dbutils.widgets.get("3. Destination Registry URI")

dbutils.widgets.text("4. Description", "") 
description = dbutils.widgets.get("4. Description")
description = description or None

dbutils.widgets.text("5. Alias", "") 
alias = dbutils.widgets.get("5. Alias")

print("src_model_uri:   ", src_model_uri)
print("dst_model_name:  ", dst_model_name)
print("dst_registry_uri:", dst_registry_uri)
print("description:", description)
print("alias:", alias)

# COMMAND ----------

# MAGIC %md ##### Set the destination model registry URI

# COMMAND ----------

if "." in src_model_uri:
    mlflow.set_registry_uri("databricks-uc")
else:
    mlflow.set_registry_uri("databricks")
    
src_client = mlflow.MlflowClient()
dst_client = mlflow.MlflowClient(registry_uri=dst_registry_uri)

print("src_client._registry_uri:", src_client._registry_uri)
print("dst_client._registry_uri:", dst_client._registry_uri)
print("mlflow.registry_uri:     ", mlflow.get_registry_uri())

# COMMAND ----------

# MAGIC %md ##### Create registered model if necessary

# COMMAND ----------

try:
    dst_client.create_registered_model(dst_model_name)
except Exception as e:
    pass

# COMMAND ----------

# MAGIC %md ##### Get source model version

# COMMAND ----------

if src_model_uri.startswith("models:"):
    toks = src_model_uri.split("/")
    model_name, version = toks[1], toks[2]
    src_vr = src_client.get_model_version(model_name, version)
    tags = src_vr.tags
    if not description:
        description = src_vr.description
else:
    tags = None
print("description: ", description)
print("tags: ", tags)

# COMMAND ----------

# MAGIC %md ##### Create model version

# COMMAND ----------

dst_vr = dst_client.create_model_version(dst_model_name, src_model_uri, description=description, tags=tags)
print(dst_vr)

# COMMAND ----------

if alias:
    dst_client.set_registered_model_alias(dst_vr.name, alias, dst_vr.version)
    dst_vr = dst_client.get_model_version(dst_vr.name, dst_vr.version)

# COMMAND ----------

print("Version:", dst_vr.version)
print("Aliases:", dst_vr.aliases)
