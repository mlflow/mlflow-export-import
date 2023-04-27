# Databricks notebook source
# Create standard .databrickscfg in custom location and specify with $DATABRICKS_CONFIG_FILE

def create_databrick_config_file(secrets_scope, secrets_key, databricks_config_file=None):
    """ Create a .databrickscfg file so you can work in shell mode with Python scripts. """
    context = dbutils.notebook.entry_point.getDbutils().notebook().getContext()
    token = dbutils.secrets.get(scope=secrets_scope, key=secrets_key)
    host_name = context.tags().get("browserHostName").get()
    user = context.tags().get("user").get()

    import os
    if not databricks_config_file:
        databricks_config_file = os.path.join("/tmp", f".databrickscfg-{user}")
    print(f"DATABRICKS_CONFIG_FILE: {databricks_config_file}")
    os.environ["DATABRICKS_CONFIG_FILE"] = databricks_config_file
    dbutils.fs.put(f"file:///{databricks_config_file}",f"[DEFAULT]\nhost=https://{host_name}\ntoken = "+token,overwrite=True)

# COMMAND ----------

def assert_widget(value, name):
    if len(value.rstrip())==0:
        raise Exception(f"ERROR: '{name}' widget is required")

# COMMAND ----------

assert_widget(secrets_scope, "1. Secrets scope")
assert_widget(secrets_token_key, "2. Secrets PAT key")

# COMMAND ----------

create_databrick_config_file(secrets_scope, secrets_token_key)

# COMMAND ----------

# MAGIC %pip install git+https:///github.com/mlflow/mlflow-export-import/#egg=mlflow-export-import

# COMMAND ----------

# MAGIC %sh mlflow --version
