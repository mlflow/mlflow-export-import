# Databricks notebook source
# DBTITLE 1,Libs
import mlflow

# COMMAND ----------

# DBTITLE 1,variables
dbutils.widgets.dropdown("mlflow_model_registry", "workspace",["workspace", "unity_catalog"])
model_registry = dbutils.widgets.get("mlflow_model_registry")

# set up mlflow model registry uri
if model_registry == "workspace":
  mlflow.set_registry_uri("databricks")
elif model_registry == "unity_catalog":
  mlflow.set_registry_uri("databricks-uc")
else:
  raise Exception("Invalid model registry")

# COMMAND ----------

# DBTITLE 1,execute
for model in mlflow.search_registered_models():
  if (model_registry == "unity_catalog" and model.name.startswith("ds_nonprod.migrated_models")) or model_registry == "workspace": 
    result = dbutils.notebook.run("get-model-hash", -1, {"registered-model-name": model.name, "mlflow_model_registry": model_registry})
    print(result)

# COMMAND ----------


