# Databricks notebook source
# Common - copy

# COMMAND ----------

# MAGIC %pip install git+https:///github.com/mlflow/mlflow-export-import@issue-138-copy-model-version#egg=mlflow-export-import

# COMMAND ----------

from mlflow_export_import.copy.local_utils import dump_obj

# COMMAND ----------

def assert_widget(value, name):
    if len(value.rstrip())==0: 
        raise Exception(f"ERROR: '{name}' widget is required")
