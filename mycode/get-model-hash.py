# Databricks notebook source
# MAGIC %md
# MAGIC This notebook takes the name of a registered mlflow model and hashes its `champion` or `Production` version, depending on whether it's in Azure (Databricks Workspace) or AWS (Unity Catalog).
# MAGIC
# MAGIC 1. The directory of the `champion`/`Production` model is exported to the local machine with MLflow artifact utilities 
# MAGIC 1. From this directory, hash the first file that ends with `pkl`

# COMMAND ----------

# MAGIC %md ## Libs

# COMMAND ----------

import mlflow
from mlflow import MlflowClient
from hashlib import md5 
import os

# COMMAND ----------

# MAGIC %md ## Setup

# COMMAND ----------

# DBTITLE 1,utils
def hash(path: str):
  with open(path,"rb") as f:
    return md5(f.read()).hexdigest()
  
def hash_model_directory(model_dir):
  try:
    fname = [file for file in os.listdir(model_dir) if file.endswith("pkl")][0]
    model_hash = hash(model_dir+fname)
    result = f"{model_name}: {model_hash}"
  except:
    result = f"{model_name}: Model file not found"
  return result

# COMMAND ----------

# DBTITLE 1,variables
dbutils.widgets.text("registered-model-name","")
model_name = dbutils.widgets.get("registered-model-name")

dbutils.widgets.dropdown("mlflow_model_registry", "workspace",["workspace", "unity_catalog"])
model_registry = dbutils.widgets.get("mlflow_model_registry")

# COMMAND ----------

# DBTITLE 1,dependent variables
if model_registry == "workspace":
  mlflow.set_registry_uri("databricks")
elif model_registry == "unity_catalog":
  mlflow.set_registry_uri("databricks-uc")
else:
  raise Exception("Invalid model registry")

if model_registry == "workspace":
  client=mlflow.tracking.MlflowClient()
  try:
    version = client.get_latest_versions(model_name, stages=["Production"])[0].version
    model_uri = f"models:/{model_name}/{version}"
  except:
    model_uri = ""
else:
  model_uri = f"models:/{model_name}@champion"

# COMMAND ----------

# MAGIC %md ## Execute

# COMMAND ----------

try:
  model_dir = mlflow.artifacts.download_artifacts(model_uri)
  result = hash_model_directory(model_dir)
except:
  result = f"{model_name}: Model not found"

# COMMAND ----------

dbutils.notebook.exit(result)

# COMMAND ----------


