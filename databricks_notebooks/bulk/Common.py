# Databricks notebook source
# MAGIC %sh 
# MAGIC #pip install mlflow-export-import
# MAGIC pip install git+https:///github.com/mlflow/mlflow-export-import/#egg=mlflow-export-import

# COMMAND ----------

import mlflow
mlflow_client = mlflow.MlflowClient()
print("MLflow version",mlflow.__version__)

# COMMAND ----------

def assert_widget(value, name):
    if len(value.rstrip())==0: 
        raise Exception(f"ERROR: '{name}' widget is required")

# COMMAND ----------

def get_notebook_formats(num):
    widget_name = f"{num}. Notebook formats"
    all_notebook_formats = [ "SOURCE", "DBC", "HTML", "JUPYTER" ]
    dbutils.widgets.multiselect(widget_name, all_notebook_formats[0], all_notebook_formats)
    notebook_formats = dbutils.widgets.get(widget_name)
    notebook_formats = notebook_formats.split(",")
    if "" in notebook_formats: notebook_formats.remove("")
    return notebook_formats
