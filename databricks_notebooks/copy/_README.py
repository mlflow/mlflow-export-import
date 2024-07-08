# Databricks notebook source
# MAGIC %md ## MLflow Export Import - Copy Notebooks
# MAGIC
# MAGIC Copy an MLflow object to either the current or to another workspace and/or model registry.
# MAGIC
# MAGIC ##### Core Notebooks
# MAGIC * [Copy_Model_Version]($Copy_Model_Version) - Copy an MLflow model model version (deep copy).
# MAGIC   * [Test_Copy_Model_Version]($tests/Test_Copy_Model_Version)
# MAGIC * [Copy_Run]($Copy_Run) - Copy an MLflow run.
# MAGIC * [Common]($Common) - Common utilities.
# MAGIC
# MAGIC ##### MLflow Copy Model Version
# MAGIC * [MLflow_Copy_Model_Version]($MLflow_Copy_Model_Version) - notebook
# MAGIC * Uses the standard [MlflowClient.copy_model_version](https://mlflow.org/docs/latest/python_api/mlflow.client.html#mlflow.client.MlflowClient.copy_model_version) method.
# MAGIC * Does not use mlflow-export-import.
# MAGIC
# MAGIC ##### Create Model Version
# MAGIC * [Create_Model_Version]($Create_Model_Version) - notebook
# MAGIC   * Creates a model version from an MLflow model "source" URI in the current or in another model registry.
# MAGIC   * Does not use mlflow-export-import.
# MAGIC * Supported sources:
# MAGIC   * MLflow Registry: `models:/my_catalog.my_schema.my_model/1` 
# MAGIC   * MLflow Run: `runs:/319a3eec9fb444d4a70996091b31a940/model` 
# MAGIC   * Volume: `/Volumes/andre_catalog/volumes/mlflow_export_import/single/sklearn_wine_best/run/artifacts/model`
# MAGIC   * DBFS: `/dbfs/home/andre@databricks.com/mlflow_export_import/single/sklearn_wine_best/model`
# MAGIC   * Local: `/root/sample_model`
# MAGIC   * Cloud: `s3:/my-bucket/mlflow-models/sklearn-wine_best`
# MAGIC
# MAGIC ##### Last updated: _2024-07-07_
