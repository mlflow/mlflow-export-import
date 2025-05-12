# Databricks notebook source
import mlflow 
from mlflow import MlflowClient
client = MlflowClient()

# COMMAND ----------

for mod in client.search_registered_models():
  model_name = mod.name

  model_uri = f"models:/{model_name}/Production"

  model = mlflow.pyfunc.load_model(model_uri=model_uri)

# COMMAND ----------


