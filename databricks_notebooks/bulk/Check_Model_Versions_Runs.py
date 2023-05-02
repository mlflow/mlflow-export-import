# Databricks notebook source
# MAGIC %md ## Check Model Versions Runs
# MAGIC
# MAGIC Check if versions runs are deleted. 
# MAGIC * Soft delete - run is marked as `deleted`(tombstoned)  but still exists in database for 30 days
# MAGIC * Hard delete - run has been physically deleted
# MAGIC
# MAGIC Widget:
# MAGIC * `1. Models`
# MAGIC * `2. Export latest versions`
# MAGIC   * `yes`: get only latest versions per stage
# MAGIC   * `no`: get all versions for all stages
# MAGIC * `3. Bail`

# COMMAND ----------

# MAGIC %run ./Common

# COMMAND ----------

dbutils.widgets.text("1. Models", "") 
models = dbutils.widgets.get("1. Models")

dbutils.widgets.dropdown("2. Export latest versions","yes",["yes","no"])
export_latest_versions = dbutils.widgets.get("2. Export latest versions") == "yes"

dbutils.widgets.text("3. Bail", "") 
bail = dbutils.widgets.get("3. Bail")
bail = None if bail=="" else int(bail) 

print("models:", models)
print("export_latest_versions:", export_latest_versions)
print("bail:", bail)

# COMMAND ----------

 assert_widget(models, "1. Models")

# COMMAND ----------

from mlflow_export_import.bulk.check_model_version_runs import mk_pandas_df

pdf = mk_pandas_df(
    models, 
    export_latest_versions=export_latest_versions, 
    bail=bail
)
df = spark.createDataFrame(pdf)
display(df)

# COMMAND ----------

df.count()

# COMMAND ----------


