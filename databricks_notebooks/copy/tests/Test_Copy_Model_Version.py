# Databricks notebook source
# MAGIC %md ### Test Copy_Model_Version notebook
# MAGIC
# MAGIC Test `Copy_Model_Version` notebook for following use cases:
# MAGIC * WS model to WS model
# MAGIC * WS model to UC model
# MAGIC * UC model to UC model
# MAGIC * UC model to WS model
# MAGIC
# MAGIC Abbreviations:
# MAGIC * WS: Workspace
# MAGIC * UC: Unity Catalog
# MAGIC
# MAGIC Last updated: 2023-10-14

# COMMAND ----------

# MAGIC %md #### Setup

# COMMAND ----------

dbutils.widgets.text("1a. Source Model WS", "") 
src_model_name_ws = dbutils.widgets.get("1a. Source Model WS")

dbutils.widgets.text("1b. Source Model Version WS", "1") 
src_model_version_ws = dbutils.widgets.get("1b. Source Model Version WS")

dbutils.widgets.text("1c. Destination Model WS", "") 
dst_model_name_ws = dbutils.widgets.get("1c. Destination Model WS")


dbutils.widgets.text("2a. Source Model UC", "") 
src_model_name_uc = dbutils.widgets.get("2a. Source Model UC")

dbutils.widgets.text("2b. Source Model Version UC", "1") 
src_model_version_uc = dbutils.widgets.get("2b. Source Model Version UC")

dbutils.widgets.text("2c. Destination Model UC", "") 
dst_model_name_uc = dbutils.widgets.get("2c. Destination Model UC")


dbutils.widgets.text("3a. Destination Experiment", "") 
dst_experiment = dbutils.widgets.get("3a. Destination Experiment")

dbutils.widgets.text("3b. Destination Run Workspace", "") 
dst_run_workspace = dbutils.widgets.get("3. Destination Run Workspace")

# COMMAND ----------

print("src_model_name_ws:", src_model_name_ws)
print("src_model_version_ws:", src_model_version_ws)
print("dst_model_name_ws:", dst_model_name_ws)

print("src_model_name_uc:", src_model_name_uc)
print("src_model_version_uc:", src_model_version_uc)
print("dst_model_name_uc:", dst_model_name_uc)

print("dst_experiment:", dst_experiment)
print("dst_run_workspace:", dst_run_workspace)

# COMMAND ----------

notebook = "../Copy_Model_Version"

common_params = {
    "4. Destination experiment name": dst_experiment,
    "5. Destination Run Workspace": dst_run_workspace,
    "6. Copy lineage tags": "no",
    "8. Return result": "yes"
}
notebook, common_params

# COMMAND ----------

def run_notebook(params):
    result = dbutils.notebook.run(notebook, 600,  params | common_params)
    print(result)

# COMMAND ----------

# MAGIC %md #### 1. WS model to WS model

# COMMAND ----------

params = {
  "1. Source Model": src_model_name_ws,
  "2. Source Version": src_model_version_ws,
  "3. Destination Model": dst_model_name_ws,
}
run_notebook(params)

# COMMAND ----------

# MAGIC %md #### 2. WS model to UC model

# COMMAND ----------

params = {
  "1. Source Model": src_model_name_ws,
  "2. Source Version": src_model_version_ws,
  "3. Destination Model": dst_model_name_uc
}
run_notebook(params)

# COMMAND ----------

# MAGIC %md #### 3. UC model to UC model

# COMMAND ----------

params = {
  "1. Source Model": src_model_name_uc,
  "2. Source Version": src_model_version_uc,
  "3. Destination Model": dst_model_name_uc
}
run_notebook(params)

# COMMAND ----------

# MAGIC %md #### 4. UC model to WS model

# COMMAND ----------

params = {
  "1. Source Model": src_model_name_uc,
  "2. Source Version": src_model_version_uc,
  "3. Destination Model": dst_model_name_ws
}
run_notebook(params)
