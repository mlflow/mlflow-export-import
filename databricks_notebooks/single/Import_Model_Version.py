# Databricks notebook source
# MAGIC %md ### Import Model Version
# MAGIC
# MAGIC ##### Overview
# MAGIC
# MAGIC * Import a registered model version.
# MAGIC * See notebook [Export_Model_Version]($Export_Model_Version).
# MAGIC
# MAGIC ##### Widgets
# MAGIC * `1. Input directory` - Input directory containing an exported model version.
# MAGIC * `2. Model name` - registered model where into which the version will be imported.
# MAGIC * `3. Destination experiment name` - contains imported run created for the model version.
# MAGIC * `4. Create model` - Create an empty registered model before creating model version.
# MAGIC * `5. Import stages and aliases` - Import stages and aliases.
# MAGIC * `6. Import metadata` - Import registered model and experiment metadata (description and tags).
# MAGIC * `7. Import source tags` - Import source information for registered model and its versions and tags destination object.

# COMMAND ----------

# MAGIC %md ### Include setup

# COMMAND ----------

# MAGIC %run ./Common

# COMMAND ----------

# MAGIC %md ### Widget setup

# COMMAND ----------

dbutils.widgets.text("1. Input directory", "") 
input_dir = dbutils.widgets.get("1. Input directory")

dbutils.widgets.text("2. Model name", "") 
model_name = dbutils.widgets.get("2. Model name")

dbutils.widgets.text("3. Destination experiment name", "") 
experiment_name = dbutils.widgets.get("3. Destination experiment name")

dbutils.widgets.dropdown("4. Create destination model","no",["yes","no"])
create_model = dbutils.widgets.get("4. Create destination model") == "yes"

dbutils.widgets.dropdown("5. Import stages and aliases","no",["yes","no"])
import_stages_and_aliases = dbutils.widgets.get("5. Import stages and aliases") == "yes"

dbutils.widgets.dropdown("6. Import metadata","no",["yes","no"])
import_metadata = dbutils.widgets.get("6. Import metadata") == "yes"

dbutils.widgets.dropdown("7. Import source tags","no",["yes","no"])
import_source_tags = dbutils.widgets.get("7. Import source tags") == "yes"

print("model_name:", model_name)
print("input_dir:", input_dir)
print("experiment_name:", experiment_name)
print("create_model:", create_model)
print("import_stages_and_aliases:", import_stages_and_aliases)
print("import_metadata:", import_metadata)
print("import_source_tags:", import_source_tags)

import os
os.environ["INPUT_DIR"] = mk_local_path(input_dir)

# COMMAND ----------

assert_widget(input_dir, "1. Input directory")
assert_widget(model_name, "2. Model version")
assert_widget(experiment_name, "3. Destination experiment name")

# COMMAND ----------

# MAGIC %md ### Turn on Unity Catalog mode if necessary

# COMMAND ----------

activate_unity_catalog(model_name)

# COMMAND ----------

# MAGIC %md ### Display model version files to be imported

# COMMAND ----------

# MAGIC %sh ls -l $INPUT_DIR

# COMMAND ----------

# MAGIC %sh cat $INPUT_DIR/model_version.json

# COMMAND ----------

# MAGIC %md ### Import model version

# COMMAND ----------

from mlflow_export_import.model_version.import_model_version import import_model_version

dst_vr = import_model_version(
    input_dir = input_dir, 
    model_name =model_name, 
    experiment_name = experiment_name, 
    create_model = create_model,
    import_stages_and_aliases = import_stages_and_aliases,
    import_metadata = import_metadata,
    import_source_tags = import_source_tags
)

# COMMAND ----------

dump_obj(dst_vr)

# COMMAND ----------

# MAGIC %md ### Display UI links

# COMMAND ----------

display_registered_model_uri(model_name)

# COMMAND ----------

display_registered_model_uri(model_name)

# COMMAND ----------

display_experiment_info(experiment_name)

# COMMAND ----------

run = mlflow_client.get_run(dst_vr.run_id)
exp = mlflow_client.get_experiment(run.info.experiment_id)
dump_obj(exp)
