# Databricks notebook source
# MAGIC %config Completer.use_jedi=False

# COMMAND ----------

# DBTITLE 1,upgrade pip
# MAGIC %sh
# MAGIC /databricks/python3/bin/python -m pip install --upgrade pip

# COMMAND ----------

# DBTITLE 1,install latest pkg from github
# MAGIC %sh 
# MAGIC #pip install mlflow-export-import
# MAGIC pip install git+https:///github.com/mlflow/mlflow-export-import/#egg=mlflow-export-import

# COMMAND ----------

# DBTITLE 1,specific installs
# MAGIC %sh
# MAGIC pip install numpy==1.22.0

# COMMAND ----------

# DBTITLE 1,we can see the s3 mount from %sh :)
# MAGIC %sh ls /dbfs/mnt/ccidsdatascidatalake/

# COMMAND ----------

dbutils.widgets.text("registered-model-name","")
model_name = dbutils.widgets.get("registered-model-name")

# COMMAND ----------

# DBTITLE 1,set env vars
import os 
from datetime import datetime
import pytz

# cst = pytz.timezone('US/Central')
# now = datetime.now(tz=cst)
# date = now.strftime("%Y%m%d_%H%M")
 
# logfile = f"/dbfs/mnt/public-blobs/dcoles/export_models_{date}.log"
# os.environ["MLFLOW_EXPORT_IMPORT_LOG_OUTPUT_FILE"] = logfile 

os.environ["MLFLOW_EXPORT_IMPORT_LOG_FORMAT"]="%(threadName)s-%(levelname)s-%(message)s"

os.environ["MLFLOW_TRACKING_URI"]="databricks"

os.environ["MLFLOW_MODEL_NAME"]=model_name

with open("/dbfs/FileStore/shared_uploads/darrell.coles@crowncastle.com/aws_databricks_credentials") as f:
  os.environ["DATABRICKS_HOST"]  = f.readline().strip("\n")
  os.environ["DATABRICKS_TOKEN"] = f.readline().strip("\n")

# COMMAND ----------

# DBTITLE 1,verify env vars
# MAGIC %sh
# MAGIC # echo $MLFLOW_EXPORT_IMPORT_LOG_OUTPUT_FILE
# MAGIC echo $MLFLOW_EXPORT_IMPORT_LOG_FORMAT
# MAGIC echo $MLFLOW_TRACKING_URI
# MAGIC echo $MLFLOW_MODEL_NAME
# MAGIC # echo $DATABRICKS_HOST
# MAGIC # echo $DATABRICKS_TOKEN

# COMMAND ----------

# DBTITLE 0,`export-models` options
# MAGIC %sh  
# MAGIC export-model --help

# COMMAND ----------

# DBTITLE 1,cli execution
# MAGIC %sh 
# MAGIC export-model \
# MAGIC   --model $MLFLOW_MODEL_NAME\
# MAGIC   --output-dir /dbfs/mnt/ccidsdatascidatalake/mlflow-migration-validation/$MLFLOW_MODEL_NAME \
# MAGIC   --stages 'Production' \
# MAGIC   --notebook-formats SOURCE

# COMMAND ----------

run_ids = [f.name.strip("/") for f in dbutils.fs.ls(f"/mnt/ccidsdatascidatalake/mlflow-migration-validation/{model_name}") if "json" not in f.name]

# TODO: logic to deal with multiple production models
run_id=run_ids[0]

model_dir = f"/mnt/ccidsdatascidatalake/mlflow-migration-validation/{model_name}/{run_id}/artifacts/model"

print(run_ids)
print(model_dir)

# COMMAND ----------

# DBTITLE 1,hash model directory
from hashlib import md5 

filenames = ["conda.yaml", "MLmodel", "model.pkl", "requirements.txt"]

def hash(path: str):
  with open(path,"rb") as f:
    return md5(f.read()).hexdigest()
  
hashes = ""
for fname in filenames:
  path = f"/dbfs/{model_dir}/{fname}"
  hashes += hash(path)

exec(f"bhashes = b'{hashes}'")

md5(bhashes).hexdigest()

# COMMAND ----------


