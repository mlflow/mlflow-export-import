# Databricks notebook source
# MAGIC %md ## Import Models
# MAGIC
# MAGIC Widgets 
# MAGIC * `1. Input directory` - directory of exported models. 
# MAGIC * `2. Delete model` - delete the current contents of model
# MAGIC * `3. Model rename file` - Model rename file.
# MAGIC * `4. Experiment rename file` - Experiment rename file.
# MAGIC * `5. Import source tags`
# MAGIC * `6. Use threads` - use multi-threaded import
# MAGIC
# MAGIC See https://github.com/mlflow/mlflow-export-import/blob/master/README_bulk.md#Import-registered-models

# COMMAND ----------

# MAGIC %run ./Common

# COMMAND ----------

dbutils.widgets.text("1. Input directory", "") 
input_dir = dbutils.widgets.get("1. Input directory")
input_dir = input_dir.replace("dbfs:","/dbfs")

dbutils.widgets.dropdown("2. Delete model","no",["yes","no"])
delete_model = dbutils.widgets.get("2. Delete model") == "yes"

dbutils.widgets.text("3. Model rename file","")
val = dbutils.widgets.get("3. Model rename file") 
model_rename_file = val or None 

dbutils.widgets.text("4. Experiment rename file","")
val = dbutils.widgets.get("4. Experiment rename file") 
experiment_rename_file = val or None 

dbutils.widgets.dropdown("5. Import source tags","no",["yes","no"])
import_source_tags = dbutils.widgets.get("5. Import source tags") == "yes"

dbutils.widgets.dropdown("6. Use threads","no",["yes","no"])
use_threads = dbutils.widgets.get("6. Use threads") == "yes"

print("input_dir:", input_dir)
print("delete_model:", delete_model)
print("model_rename_file:     ", model_rename_file)
print("experiment_rename_file:", experiment_rename_file)
print("import_source_tags:", import_source_tags)
print("use_threads:", use_threads)

# COMMAND ----------

assert_widget(input_dir, "1. Input directory")

# COMMAND ----------

# MAGIC %%capture captured
# MAGIC
# MAGIC from mlflow_export_import.bulk.import_models import import_models
# MAGIC
# MAGIC import_models(
# MAGIC     input_dir = input_dir,
# MAGIC     delete_model = delete_model,
# MAGIC     use_src_user_id = True,
# MAGIC     import_source_tags = import_source_tags,
# MAGIC     experiment_renames = experiment_rename_file,
# MAGIC     model_renames = model_rename_file,
# MAGIC     use_threads = use_threads
# MAGIC )

# COMMAND ----------

# DBTITLE 1,write log file
filepath = "/mnt/public-blobs/dcoles/mlflow_import_models_log.txt"

dbutils.fs.rm(filepath)
dbutils.fs.put(filepath, captured.stdout)
