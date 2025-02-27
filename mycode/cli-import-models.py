# Databricks notebook source
#md ## Libs

# COMMAND ----------

# DBTITLE 1,install latest pkg from github
# MAGIC %sh 
# MAGIC #pip install mlflow-export-import
# MAGIC pip install git+https:///github.com/mlflow/mlflow-export-import/#egg=mlflow-export-import

# COMMAND ----------

# DBTITLE 1,we can see the s3 mount from %sh :)
# MAGIC %sh ls /dbfs/mnt/datalake/

# COMMAND ----------

# MAGIC %run ./credentials

# COMMAND ----------

# MAGIC %md ## Setup

# COMMAND ----------

dbutils.widgets.dropdown("platform","",["", "azure", "aws"])
platform = dbutils.widgets.get("platform")

credentials_path = get_credentials_path(platform)

# COMMAND ----------

# DBTITLE 1,set env vars
import os 
from datetime import datetime
import pytz

cst = pytz.timezone('US/Central')
now = datetime.now(tz=cst)
date = now.strftime("%Y%m%d_%H%M")
 
logfile = f"import_models_{date}.log"
os.environ["MLFLOW_EXPORT_IMPORT_LOG_OUTPUT_FILE"] = logfile 

os.environ["MLFLOW_EXPORT_IMPORT_LOG_FORMAT"]="%(threadName)s-%(levelname)s-%(message)s"

os.environ["MLFLOW_TRACKING_URI"]="databricks"

with open(credentials_path) as f:
  os.environ["DATABRICKS_HOST"]  = f.readline().strip("\n")
  os.environ["DATABRICKS_TOKEN"] = f.readline().strip("\n")

# COMMAND ----------

# DBTITLE 1,verify env vars
# MAGIC %sh
# MAGIC echo $MLFLOW_EXPORT_IMPORT_LOG_OUTPUT_FILE
# MAGIC echo $MLFLOW_EXPORT_IMPORT_LOG_FORMAT
# MAGIC echo $MLFLOW_TRACKING_URI
# MAGIC #echo $DATABRICKS_HOST
# MAGIC #echo $DATABRICKS_TOKEN

# COMMAND ----------

# DBTITLE 0,`export-models` options
# MAGIC %sh 
# MAGIC import-models --help

# COMMAND ----------

# MAGIC %md ## Execution

# COMMAND ----------

# DBTITLE 1,cli execution
# MAGIC %sh 
# MAGIC import-models \
# MAGIC   --input-dir /dbfs/mnt/datalake/mlflow-migration-models \
# MAGIC   --delete-model True \
# MAGIC   --import-permissions True \
# MAGIC   --import-source-tags True \
# MAGIC   --verbose True
# MAGIC   --use-threads False

# COMMAND ----------

# MAGIC %md ## Appendices

# COMMAND ----------

# DBTITLE 1,count models in workspace model registry
import mlflow
len(mlflow.search_registered_models())

# COMMAND ----------

# MAGIC %sh
# MAGIC import-model --help

# COMMAND ----------

# MAGIC %sh 
# MAGIC import-model \
# MAGIC   --input-dir /dbfs/mnt/ccidsdatascidatalake/mlflow-migration-models/models/pycaret_small_cell_clf \
# MAGIC   --model pycaret_small_cell_clf \
# MAGIC   --experiment-name /Users/darrell.coles@crowncastle.com/databricks_automl/pycaret-sc-clf-test-1 \
# MAGIC   --delete-model True \
# MAGIC   # --import-permissions True \
# MAGIC   --import-source-tags True \
# MAGIC   --verbose True

# COMMAND ----------

# MAGIC %sh cat /dbfs/mnt/ccidsdatascidatalake/mlflow-migration-models/models/models.json

# COMMAND ----------

def get_most_recent_experiment_name(model):
  try:
    newest = max(model["mlflow"]["registered_model"]["versions"], key=lambda v:v["last_updated_timestamp"])
    return newest["_experiment_name"]
  except:
    return None

# COMMAND ----------

import json

input_dir = "/dbfs/mnt/ccidsdatascidatalake/mlflow-migration-models/models" 

with open(f"{input_dir}/models.json") as f:
  models = json.load(f)
  model_names = models["info"]["model_names"]

with open("model_experiment","w") as model_experiment:
  for m in model_names:
    with open(f"{input_dir}/{m}/model.json") as f:
      model = json.load(f)
      experiment_name = get_most_recent_experiment_name(model)
      if experiment_name:
        model_experiment.write(f"{m},{experiment_name}\n")

# COMMAND ----------

# MAGIC %sh cat model_experiment

# COMMAND ----------

# MAGIC %sh 
# MAGIC
# MAGIC input_dir=/dbfs/mnt/ccidsdatascidatalake/mlflow-migration-models/models
# MAGIC
# MAGIC while IFS=, read model experiment; 
# MAGIC do 
# MAGIC   import-model \
# MAGIC     --input-dir $input_dir/$model \
# MAGIC     --model $model \
# MAGIC     --experiment-name $experiment_name \
# MAGIC     --delete-model True \
# MAGIC     --import-source-tags True \
# MAGIC     --verbose True;
# MAGIC done < model_experiment

# COMMAND ----------

# MAGIC %sh
# MAGIC while IFS=, read field1 field2;
# MAGIC   do 
# MAGIC     echo model: $field1
# MAGIC     echo experiment: $field2
# MAGIC done < model_experiment

# COMMAND ----------

import os
os.environ

# COMMAND ----------

# MAGIC %sh $elas

# COMMAND ----------


