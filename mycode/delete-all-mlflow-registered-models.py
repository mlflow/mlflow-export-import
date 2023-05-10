# Databricks notebook source
from mlflow import MlflowClient
client = MlflowClient()

# COMMAND ----------

for mod in client.search_registered_models():
  name = mod.name

  # transition all stages to 'Archived'
  dbutils.notebook.run("./set-all-registered-model-stages-to-archived", -1, {"model_name": name})

  # delete registered model
  client.delete_registered_model(name)

# COMMAND ----------


