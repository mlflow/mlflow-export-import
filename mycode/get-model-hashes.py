# Databricks notebook source
# MAGIC %config Completer.use_jedi=False

# COMMAND ----------

import mlflow

for model in mlflow.search_registered_models():
  result = dbutils.notebook.run("get-model-hash", -1, {"registered-model-name": model.name})
  print(result)

# COMMAND ----------


