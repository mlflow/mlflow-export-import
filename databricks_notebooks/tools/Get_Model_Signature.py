# Databricks notebook source
# MAGIC %md ### Get Model Signature 
# MAGIC
# MAGIC Get the signature of an MLflow model. 
# MAGIC
# MAGIC ##### MLflow models can live in a variety of places. Sample MLflow model URIs:
# MAGIC * `models:/andre_catalog.ml_models2.sklearn_wine_best/15`
# MAGIC * `models:/Sklearn_Wine_best/1`
# MAGIC * `runs:/030075d9727945259c7d283e47fee4a9/model`
# MAGIC * `/Volumes/andre_catalog/volumes/mlflow_export_import/single/sklearn_wine_best/run/artifacts/model`
# MAGIC * `/dbfs/home/first.last@databricks.com/mlflow_export_import/single/sklearn_wine_best/model`
# MAGIC * `s3:/my-bucket/mlflow-models/sklearn_wine_best`
# MAGIC
# MAGIC ##### The signature is located in the MLmodel artifact of the MLflow model.
# MAGIC * For a run, you can view the signature in the "Artifacts" tab of the run UI page.
# MAGIC * For a model version, you can only view (in the UI) the signature via the run.
# MAGIC   * To get the actual signature of the deployed model, you need to use the API method `mlflow.models.get_model_info()`.
# MAGIC
# MAGIC ##### Documentation:
# MAGIC * [mlflow.models.ModelSignature](https://mlflow.org/docs/latest/python_api/mlflow.models.html#mlflow.models.ModelSignature)
# MAGIC * [mlflow.models.get_model_info](https://mlflow.org/docs/latest/python_api/mlflow.models.html#mlflow.models.get_model_info)

# COMMAND ----------

# MAGIC %md #### Setup

# COMMAND ----------

# MAGIC %run ./Common

# COMMAND ----------

dbutils.widgets.text("Model URI", "")
model_uri = dbutils.widgets.get("Model URI")
print("model_uri:", model_uri)

# COMMAND ----------

assert_widget(model_uri, "Model URI")
set_registry_uri(model_uri)

# COMMAND ----------

# MAGIC %md #### Get `model_info.signature`

# COMMAND ----------

model_info = mlflow.models.get_model_info(model_uri)
model_info.signature

# COMMAND ----------

if not model_info.signature:
    print(f"Model '{model_uri}' does not have a signature")
    dbutils.notebook.exit(None)

# COMMAND ----------

dump_json(model_info.signature.to_dict())

# COMMAND ----------

# MAGIC %md #### Display "stringified" signature as JSON

# COMMAND ----------

signature = to_json_signature(model_info.signature.to_dict())
dump_json(signature)
