# Databricks notebook source
# MAGIC %md ### List Model Versions Without Signature
# MAGIC
# MAGIC #### Widgets
# MAGIC * `1. Filter` - Filter is for  search_registered_models()
# MAGIC * `2. Output file` - save output as CSV file
# MAGIC
# MAGIC List Workspace Model Registry model version that don't have a signature

# COMMAND ----------

# MAGIC %pip install -U mlflow-skinny
# MAGIC #%pip install -U git+https:///github.com/mlflow/mlflow-export-import/#egg=mlflow-export-import
# MAGIC %pip install -U /dbfs/home/andre.mesarovic@databricks.com/lib/wheels/mlflow_export_import-1.2.0-py3-none-any.whl
# MAGIC
# MAGIC dbutils.library.restartPython()

# COMMAND ----------

import mlflow
mlflow_client = mlflow.MlflowClient()
mlflow.set_registry_uri("databricks")
print("mlflow.version:", mlflow.__version__)

# COMMAND ----------

# name like 'Sklearn_Win%'

# COMMAND ----------

dbutils.widgets.text("1. Filter","")
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
