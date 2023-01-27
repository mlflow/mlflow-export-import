# Databricks notebook source
# MAGIC %md ### Delete registered model and its versions

# COMMAND ----------

# MAGIC %run ./Common

# COMMAND ----------

dbutils.widgets.removeAll()

dbutils.widgets.text("Registered model", "")
model = dbutils.widgets.get("Registered model")

print("model:",model)
assert_widget(model, "Registered model")

# COMMAND ----------

from mlflow_tools.tools.delete_model import delete_model
delete_model(model)