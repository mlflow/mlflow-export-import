# Databricks notebook source
# MAGIC %sh 
# MAGIC #pip install mlflow-export-import
# MAGIC #pip install git+https:///github.com/mlflow/mlflow-export-import/#egg=mlflow-export-import
# MAGIC 
# MAGIC pip install git+https:///github.com/mlflow/mlflow-export-import@issue-90-named-args#egg=mlflow-export-import

# COMMAND ----------

def assert_widget(value, name):
    if len(value.rstrip())==0: 
        raise Exception(f"ERROR: '{name}' widget is required")

# COMMAND ----------

import mlflow
mlflow_client = mlflow.client.MlflowClient()