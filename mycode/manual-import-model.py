# Databricks notebook source
# MAGIC %md ### Manually import models that failed with the `import-models` utility
# MAGIC
# MAGIC You can find which models failed by searching the import_models log for "the source run_id was probably deleted"

# COMMAND ----------

# DBTITLE 1,install latest pkg from github
# MAGIC %sh 
# MAGIC #pip install mlflow-export-import
# MAGIC pip install git+https:///github.com/mlflow/mlflow-export-import/#egg=mlflow-export-import

# COMMAND ----------

import os

# COMMAND ----------

# DBTITLE 1,set model env vars
wij = dbutils.widgets

wij.text("input_dir","/dbfs/mnt/datalake/mlflow-migration-models/models")
input_dir = wij.get("input_dir")

wij.text("model_name", "churn-model")
model_name = wij.get("model_name")

# set env variables for shell command
os.environ["INPUT_DIR"]=input_dir
os.environ["MODEL_NAME"]=model_name

# COMMAND ----------

# DBTITLE 1,set MLflow env vars
from datetime import datetime
import pytz

cst = pytz.timezone('US/Central')
now = datetime.now(tz=cst)
date = now.strftime("%Y%m%d_%H%M")
 
logfile = f"import_model_{model_name}_{date}.log"
os.environ["MLFLOW_EXPORT_IMPORT_LOG_OUTPUT_FILE"] = logfile 

os.environ["MLFLOW_EXPORT_IMPORT_LOG_FORMAT"]="%(threadName)s-%(levelname)s-%(message)s"

os.environ["MLFLOW_TRACKING_URI"]="databricks"

with open("/dbfs/FileStore/tables/aws_databricks_credentials") as f:
  os.environ["DATABRICKS_HOST"]  = f.readline().strip("\n")
  os.environ["DATABRICKS_TOKEN"] = f.readline().strip("\n")

# COMMAND ----------

# DBTITLE 1,set experiment env vars
import json

def get_most_recent_experiment_name(model: dict):
  try:
    newest = max(model["mlflow"]["registered_model"]["versions"], key=lambda v:v["last_updated_timestamp"])
    return newest["_experiment_name"]
  except:
    return None

with open(f"{input_dir}/{model_name}/model.json") as f:
  model = json.load(f)
  os.environ["EXPERIMENT_NAME"] = get_most_recent_experiment_name(model)

# COMMAND ----------

# DBTITLE 1,remove failed model registrations before import
import json
import os

fname = f"{input_dir}/{model_name}/model.json"

# read model.json
with open(fname, "r") as f:
  d = json.load(f)

# remove failed versions
for version in d["mlflow"]["registered_model"]["versions"]:
  if version["status"] == 'FAILED_REGISTRATION':
    d["mlflow"]["registered_model"]["versions"].remove(version)

# rename old json
os.rename(fname, f"{fname}_old")

# write clean json
with open(fname, "w") as f:
  d = json.dump(d, f)

# COMMAND ----------

# DBTITLE 1,verify env vars
# MAGIC %sh
# MAGIC echo $MLFLOW_EXPORT_IMPORT_LOG_OUTPUT_FILE
# MAGIC echo $MLFLOW_EXPORT_IMPORT_LOG_FORMAT
# MAGIC echo $MLFLOW_TRACKING_URI
# MAGIC echo $INPUT_DIR
# MAGIC echo $MODEL_NAME
# MAGIC echo $EXPERIMENT_NAME
# MAGIC #echo $DATABRICKS_HOST
# MAGIC #echo $DATABRICKS_TOKEN

# COMMAND ----------

# DBTITLE 0,`export-models` options
# MAGIC %sh 
# MAGIC import-model --help

# COMMAND ----------

# DBTITLE 1,cli execution
# MAGIC %sh 
# MAGIC import-model \
# MAGIC   --input-dir $INPUT_DIR/$MODEL_NAME \
# MAGIC   --model $MODEL_NAME \
# MAGIC   --experiment-name $EXPERIMENT_NAME \
# MAGIC   --delete-model True \
# MAGIC   --import-source-tags True \
# MAGIC   --verbose True

# COMMAND ----------

#%sh ls /dbfs/databricks/mlflow-tracking

# COMMAND ----------



# COMMAND ----------

# MAGIC %sh cat /dbfs/mnt/datalake/mlflow-migration-models/models/churn-arima/model.json

# COMMAND ----------


