# Databricks notebook source
# MAGIC %pip install git+https:///github.com/mlflow/mlflow-export-import/#egg=mlflow-export-import

# COMMAND ----------

# Create standard .databrickscfg in custom location and specify with $DATABRICKS_CONFIG_FILE

def create_databrick_config_file(databricks_config_file=None):
    print("TODO: configure by user")
    pass

# COMMAND ----------

create_databrick_config_file()

# COMMAND ----------

# MAGIC %sh mlflow --version
