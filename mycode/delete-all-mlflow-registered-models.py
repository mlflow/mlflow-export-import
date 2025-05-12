# Databricks notebook source
from mlflow import MlflowClient

# COMMAND ----------

dbutils.widgets.dropdown("mlflow_model_registry","",["", "unity_catalog","workspace"])
model_registry = dbutils.widgets.get("mlflow_model_registry")

client = MlflowClient(registry_uri="databricks-uc") if model_registry == "unity_catalog" else MlflowClient()

# COMMAND ----------

for model in client.search_registered_models():
  model_name = model.name
  if model_registry == "unity_catalog":
    if not model_name.startswith("ds_nonprod.migrated_models"):
      continue
  else:
    # transition all stages to 'Archived' in workspace registry
    dbutils.notebook.run("./set-all-registered-model-stages-to-archived", -1, {"model_name": model_name})

  print(f"Deleting model: {model_name}")
  client.delete_registered_model(model_name)

# COMMAND ----------


