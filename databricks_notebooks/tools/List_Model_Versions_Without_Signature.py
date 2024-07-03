# Databricks notebook source
# MAGIC %md ### List Model Versions Without Signature
# MAGIC
# MAGIC List Workspace Model Registry model version that don't have a signature.
# MAGIC
# MAGIC #### Widgets
# MAGIC * `1. Filter` - Filter is for [search_registered_models()](https://mlflow.org/docs/latest/python_api/mlflow.client.html#mlflow.client.MlflowClient.search_registered_models) such as `name like 'Sklearn_Wine%'`
# MAGIC * `2. Output file` - save output as CSV file

# COMMAND ----------

# MAGIC %run ./Common

# COMMAND ----------

import mlflow
mlflow_client = mlflow.MlflowClient()
mlflow.set_registry_uri("databricks")
print("mlflow.version:", mlflow.__version__)

# COMMAND ----------

dbutils.widgets.text("1. Filter","name like 'Sklearn_Wine%'")
filter = dbutils.widgets.get("1. Filter")
filter = filter or None

dbutils.widgets.text("2. Output file","")
output_file = dbutils.widgets.get("2. Output file")

print("filter:", filter)
print("output_file:", output_file)

# COMMAND ----------

from mlflow_export_import.tools.list_model_versions_without_signatures import as_pandas_df

df = as_pandas_df(filter)
display(df)

# COMMAND ----------

if output_file:
    with open(output_file, "w", encoding="utf-8") as f:
        df.to_csv(f, index=False)
