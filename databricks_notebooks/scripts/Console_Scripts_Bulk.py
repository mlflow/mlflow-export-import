# Databricks notebook source
# MAGIC %md ## Console Scripts - Bulk
# MAGIC 
# MAGIC * Use this notebook as a starting point template for executing console scripts.
# MAGIC * See [github.com/mlflow/mlflow-export-import/blob/master/README_bulk.md](https://github.com/mlflow/mlflow-export-import/blob/master/README_bulk.md).

# COMMAND ----------

# MAGIC %run ./Common

# COMMAND ----------

# MAGIC %md #### Experiments

# COMMAND ----------

# MAGIC %sh export-experiments --help

# COMMAND ----------

# MAGIC %sh import-experiments --help

# COMMAND ----------

# MAGIC %md #### Models

# COMMAND ----------

# MAGIC %sh export-models --help

# COMMAND ----------

# MAGIC %sh import-models --help

# COMMAND ----------

# MAGIC %md #### All

# COMMAND ----------

# MAGIC %sh export-all --help

# COMMAND ----------

# MAGIC %sh import-all --help
