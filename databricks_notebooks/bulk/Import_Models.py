# Databricks notebook source
# MAGIC %md ## Import Models
# MAGIC 
# MAGIC Widgets
# MAGIC * `1. Input directory` - directory of exported models.
# MAGIC * `2. Delete model` - delete the current contents of model
# MAGIC * `3. Import source tags`
# MAGIC * `4. Use threads` - use multi-threaded import
# MAGIC 
# MAGIC See https://github.com/mlflow/mlflow-export-import/blob/master/README_collection.md#Import-registered-models

# COMMAND ----------

# MAGIC %run ./Common

# COMMAND ----------

dbutils.widgets.text("1. Input directory", "") 
input_dir = dbutils.widgets.get("1. Input directory")
input_dir = input_dir.replace("dbfs:","/dbfs")

dbutils.widgets.dropdown("2. Delete model","no",["yes","no"])
delete_model = dbutils.widgets.get("2. Delete model") == "yes"

dbutils.widgets.dropdown("3. Import source tags","no",["yes","no"])
import_source_tags = dbutils.widgets.get("3. Import source tags") == "yes"

dbutils.widgets.dropdown("4. Use threads","no",["yes","no"])
use_threads = dbutils.widgets.get("4. Use threads") == "yes"

print("input_dir:", input_dir)
print("delete_model:", delete_model)
print("import_source_tags:", import_source_tags)
print("use_threads:", use_threads)

# COMMAND ----------

assert_widget(input_dir, "1. Input directory")

# COMMAND ----------

from mlflow_export_import.bulk.import_models import import_all

import_all(
    input_dir = input_dir,
    delete_model = delete_model,
    import_source_tags = import_source_tags,
    use_threads = use_threads
)
