# Databricks notebook source
from mlflow import MlflowClient

# COMMAND ----------

dbutils.widgets.text("model_name","")
model_name = dbutils.widgets.get("model_name")

# COMMAND ----------

client = MlflowClient()

for mv in client.search_model_versions(f"name='{model_name}'"):
  version = int(mv.version)
  if mv.current_stage != "Archived":
    try:
      client.transition_model_version_stage(name=model_name, version=version, stage="Archived")
    except:
      print(f"'{model_name}' version {version} state transition failed")

# COMMAND ----------


