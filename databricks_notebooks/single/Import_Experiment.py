# Databricks notebook source
# MAGIC %md ### Import Experiment
# MAGIC
# MAGIC **Widgets**
# MAGIC * `1. Input directory` - Input directory containing an exported experiment.
# MAGIC * `2. Destination experiment name` - will create experiment if it doesn't exist.
# MAGIC * `3. Import source tags` 

# COMMAND ----------

# MAGIC %md ### Include setup

# COMMAND ----------

# MAGIC %run ./Common

# COMMAND ----------

# MAGIC %md ### Widget setup

# COMMAND ----------


dbutils.widgets.text("1. Destination experiment name", "") 
experiment_name = dbutils.widgets.get("1. Destination experiment name")

dbutils.widgets.text("2. Input directory", "") 
input_dir = dbutils.widgets.get("2. Input directory")

dbutils.widgets.dropdown("3. Import permissions","no",["yes","no"])
import_permissions = dbutils.widgets.get("3. Import permissions") == "yes"

dbutils.widgets.dropdown("4. Import source tags","no",["yes","no"])
import_source_tags = dbutils.widgets.get("4. Import source tags") == "yes"

print("input_dir:", input_dir)
print("experiment_name:", experiment_name)
print("import_permissions:", import_permissions)
print("import_source_tags:", import_source_tags)

# COMMAND ----------

assert_widget(experiment_name, "1. Destination experiment name")
assert_widget(input_dir, "2. Input directory")

# COMMAND ----------

# MAGIC %md ### Import experiment

# COMMAND ----------

from mlflow_export_import.experiment.import_experiment import import_experiment

import_experiment(
    experiment_name = experiment_name, 
    input_dir = input_dir,
    import_permissions = import_permissions,
    import_source_tags = import_source_tags
)

# COMMAND ----------

# MAGIC %md ### Display experiment UI link

# COMMAND ----------

display_experiment_info(experiment_name)
