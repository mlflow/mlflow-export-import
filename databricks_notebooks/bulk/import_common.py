# Databricks notebook source
# DBTITLE 1,install mlflow-export-import from local
# MAGIC %pip install ../../../mlflow-export-import --use-feature=in-tree-build

# COMMAND ----------

def assert_widget(value, name):
    if len(value.rstrip())==0: 
        raise Exception(f"ERROR: '{name}' widget is required")

# COMMAND ----------

import mlflow
mlflow_client = mlflow.client.MlflowClient()
