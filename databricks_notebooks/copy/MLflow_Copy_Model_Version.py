# Databricks notebook source
# MAGIC %md ## MLflow_Copy_Model_Version
# MAGIC
# MAGIC Uses the standard `MlflowClient.copy_model_version()` method.
# MAGIC
# MAGIC ##### Widgets
# MAGIC
# MAGIC * `1. Source Model  URI` - Source model URI (must be `models:` scheme)
# MAGIC * `2. Destination Model` - Destination model name.
# MAGIC
# MAGIC #### Documentation
# MAGIC * [MlflowClient.copy_model_version](https://mlflow.org/docs/latest/python_api/mlflow.client.html#mlflow.client.MlflowClient.copy_model_version)

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

print("src_model_uri:   ", src_model_uri)
print("dst_model_name:  ", dst_model_name)

# COMMAND ----------

if "." in src_model_uri:
    mlflow.set_registry_uri("databricks-uc")
else:
    mlflow.set_registry_uri("databricks")
client = mlflow.MlflowClient()
print("client._registry_uri:", client._registry_uri)

# COMMAND ----------

dst_vr = client.copy_model_version(src_model_uri, dst_model_name)

# COMMAND ----------

dst_vr
