# Databricks notebook source
# MAGIC %pip install git+https:///github.com/mlflow/mlflow-export-import/#egg=mlflow-export-import

# COMMAND ----------

# Create standard .databrickscfg in custom location and specify with $DATABRICKS_CONFIG_FILE

def create_databrick_config_file(databricks_config_file=None):
    context = dbutils.notebook.entry_point.getDbutils().notebook().getContext()
    token = context.apiToken().get()
    host_name = context.tags().get("browserHostName").get()
    user = context.tags().get("user").get()

    import os
    if not databricks_config_file:
        databricks_config_file = os.path.join("/tmp", f".databricks.cfg-{user}")
    print(f"DATABRICKS_CONFIG_FILE: {databricks_config_file}")
    os.environ["DATABRICKS_CONFIG_FILE"] = databricks_config_file
    dbutils.fs.put(f"file:///{databricks_config_file}",f"[DEFAULT]\nhost=https://{host_name}\ntoken = "+token,overwrite=True)

# COMMAND ----------

create_databrick_config_file()

# COMMAND ----------

# MAGIC %sh mlflow --version
