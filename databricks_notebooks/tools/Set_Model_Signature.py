# Databricks notebook source
# MAGIC %md ### Set Model Signature 
# MAGIC
# MAGIC ##### Overview
# MAGIC
# MAGIC * Set the signature of a run's MLflow model.
# MAGIC * If this run model is backing a model version, you need to re-register model. 
# MAGIC
# MAGIC ##### Notes:
# MAGIC * Only models with a `runs:/` scheme are supported.
# MAGIC * If you pass a `models:/` scheme you get the following error:
# MAGIC   * Failed to set signature on "models:/Sklearn_Wine_test/5". Model URIs with the `models:/` scheme are not supported.
# MAGIC
# MAGIC ##### Widgets
# MAGIC * `1. Model URI` - Model URI - only `runs:/` scheme are supported.
# MAGIC * `2. Input table` - table with training data samples.
# MAGIC * `3. Output table` - table with prediction samples.
# MAGIC
# MAGIC ##### The signature can be found in the MLmodel artifact of the MLflow model.
# MAGIC * For a run, you can view the signature in the "Artifacts" tab of the run UI page.
# MAGIC * For a model version, you can only view (in the UI) the signature via the run.
# MAGIC   * To get the actual signature of the deployed model, you need to use the API method `mlflow.models.get_model_info()`.
# MAGIC
# MAGIC ##### Documentation:
# MAGIC * [mlflow.models.set_signature](https://mlflow.org/docs/latest/python_api/mlflow.models.html#mlflow.models.set_signature)
# MAGIC * [mlflow.models.ModelSignature](https://mlflow.org/docs/latest/python_api/mlflow.models.html#mlflow.models.ModelSignature)

# COMMAND ----------

# MAGIC %md #### Setup

# COMMAND ----------

# MAGIC %run ./Common

# COMMAND ----------

dbutils.widgets.text("1. Model URI", "")
model_uri = dbutils.widgets.get("1. Model URI")

dbutils.widgets.text("2. Input table", "")
input_table = dbutils.widgets.get("2. Input table")

dbutils.widgets.text("3. Output table", "")
output_table = dbutils.widgets.get("3. Output table")

print("model_uri:   ", model_uri)
print("input_table: ", input_table)
print("output_table:", output_table)

# COMMAND ----------

assert_widget(model_uri, "1. Model URI")
assert_widget(input_table, "2. Input table")
assert_widget(output_table, "3. Output table")

set_registry_uri(model_uri)

# COMMAND ----------

# MAGIC %md #### Check if  model signature exists

# COMMAND ----------

from mlflow_export_import.tools.signature_utils import get_model_signature
signature = get_model_signature(model_uri)
signature

# COMMAND ----------

if signature:
    dbutils.notebook.exit(f"Model '{model_uri}' already has a signature")

# COMMAND ----------

# MAGIC %md #### Read input and output tables

# COMMAND ----------

df_input = spark.table(input_table)
display(df_input.take(5))

# COMMAND ----------

df_output = spark.table(output_table)
display(df_output.take(5))

# COMMAND ----------

# MAGIC %md #### Create signature

# COMMAND ----------

from mlflow.models.signature import infer_signature
signature = infer_signature(df_input, df_output)
signature

# COMMAND ----------

signature_dct = to_json_signature(signature.to_dict())
dump_json(signature_dct)

# COMMAND ----------

# MAGIC %md #### Set model signature

# COMMAND ----------

mlflow.models.set_signature(model_uri, signature)

# COMMAND ----------

# MAGIC %md #### Get the new model signature

# COMMAND ----------

get_model_signature(model_uri)
