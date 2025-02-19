# Databricks notebook source
import mlflow
import pyspark.sql.functions as F
import pandas as pd

# COMMAND ----------

registered_models = mlflow.search_registered_models()

model_name, user_id = [], []
for model in registered_models:
  model_name.append(model.name) 
  user_id.append(model.latest_versions[0].user_id)

user_models = pd.DataFrame({'model': model_name, 'user': user_id})

# COMMAND ----------

display(
  spark.createDataFrame(user_models)
  .groupBy("user")
  .agg(F.collect_set("model").alias("models"))
  )

# COMMAND ----------


