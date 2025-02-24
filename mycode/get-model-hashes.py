# Databricks notebook source
# DBTITLE 1,Libs
import mlflow

# COMMAND ----------

# DBTITLE 1,variables
dbutils.widgets.dropdown("platform", "", ["", "azure", "aws"])
platform = dbutils.widgets.get("platform")

# COMMAND ----------

# DBTITLE 1,execute
for model in mlflow.search_registered_models():
  result = dbutils.notebook.run("get-model-hash", -1, {"registered-model-name": model.name, "platform": platform})
  print(result)

# COMMAND ----------


