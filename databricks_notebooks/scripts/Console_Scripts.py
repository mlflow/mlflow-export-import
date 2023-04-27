# Databricks notebook source
# MAGIC %md ## Console Scripts - Single
# MAGIC
# MAGIC * Use this notebook as a starting point template for executing console scripts.
# MAGIC * See [github.com/mlflow/mlflow-export-import/blob/master/README_single.md](https://github.com/mlflow/mlflow-export-import/blob/master/README_single.md).
# MAGIC * You'll first need to specify a [Databricks secret](https://docs.databricks.com/security/secrets/secrets.html) to your [PAT](https://docs.databricks.com/administration-guide/access-control/tokens.html) (personal access token) to execute CLI commands.

# COMMAND ----------

# MAGIC %md ### Setup

# COMMAND ----------

dbutils.widgets.text("1. Secrets scope", "")
secrets_scope = dbutils.widgets.get("1. Secrets scope")
dbutils.widgets.text("2. Secrets PAT key", "")
secrets_token_key = dbutils.widgets.get("2. Secrets PAT key")
secrets_scope, secrets_token_key

# COMMAND ----------

# MAGIC %run ./Common

# COMMAND ----------

# MAGIC %sh 
# MAGIC echo "DATABRICKS_CONFIG_FILE: $DATABRICKS_CONFIG_FILE"
# MAGIC cat $DATABRICKS_CONFIG_FILE

# COMMAND ----------

# MAGIC %md ### Single notebooks

# COMMAND ----------

# MAGIC %md #### Experiment

# COMMAND ----------

# MAGIC %sh export-experiment --help

# COMMAND ----------

# MAGIC %sh import-experiment --help

# COMMAND ----------

# MAGIC %md #### export-model

# COMMAND ----------

# MAGIC %sh export-model --help

# COMMAND ----------

# MAGIC %sh import-model --help

# COMMAND ----------

# MAGIC %md #### export-run

# COMMAND ----------

# MAGIC %sh export-run --help

# COMMAND ----------

# MAGIC %sh import-run --help

# COMMAND ----------

# MAGIC %md ### Bulk notebooks

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
