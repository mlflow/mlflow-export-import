# Databricks notebook source
import mlflow 
from mlflow import MlflowClient
client = MlflowClient()

# COMMAND ----------

len(client.search_registered_models())

# COMMAND ----------

count = 0

for registered_model in mlflow.search_registered_models():
  has_prod_stg = False
  if "Production" in [version.current_stage for version in registered_model.latest_versions]:
    has_prod_stg = True
    count +=1
  if not has_prod_stg:
    print(registered_model.name, "DOES NOT HAVE a Production stage")

print(count, "models have Production stage all together")

# COMMAND ----------


