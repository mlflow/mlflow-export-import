# Databricks notebook source
# MAGIC %md
# MAGIC This notebook takes the name of a registered mlflow model and hashes its `champion` or `Production` version, depending on whether it's in Azure (Databricks Workspace) or AWS (Unity Catalog).
# MAGIC
# MAGIC 1. The directory of the `champion`/`Production` model is exported to the local machine with MLflow artifact utilities 
# MAGIC 1. Several files reside in this directory. Of these, the files `conda.yaml`, `model.pkl`, and `requirements.txt` are hashed
# MAGIC 1. The 3 hashes are sorted, concatenated, and hashed again to create the final, model hash.

# COMMAND ----------

# MAGIC %md ## Libs

# COMMAND ----------

import mlflow
from mlflow import MlflowClient
from hashlib import md5 

# COMMAND ----------

# MAGIC %md ## Setup

# COMMAND ----------

# DBTITLE 1,utils
def hash(path: str):
  with open(path,"rb") as f:
    return md5(f.read()).hexdigest()
  
def hash_model_directory(model_dir):
  files = ["conda.yaml", "model.pkl", "requirements.txt"]
  try:
    hashes = []
    for file in files:
      hashes.append(hash(model_dir+file))
    hashes = sorted(hashes)
    bhashes = ''.join(hashes).encode('utf-8')
    final_hash = md5(bhashes).hexdigest()
    result = f"{model_name}: {final_hash}"
  except:
    result = f"{model_name}: Model files not found"
  return result

# COMMAND ----------

# DBTITLE 1,variables
dbutils.widgets.text("registered-model-name","")
model_name = dbutils.widgets.get("registered-model-name")

dbutils.widgets.dropdown("platform","",["","azure","aws"])
platform = dbutils.widgets.get("platform")

# COMMAND ----------

# DBTITLE 1,dependent variables
if platform == "aws":
  mlflow.set_registry_uri("databricks-uc")

model_uri = f"models:/{model_name}/Production" if platform == "azure" else f"runs:/ds_nonprod.migrated_models.{model_name}@champion"

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


