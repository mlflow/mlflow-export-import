# Databricks notebook source
# MAGIC %md ## Libs

# COMMAND ----------

# DBTITLE 1,install latest pkg from github
# MAGIC %sh 
# MAGIC #pip install mlflow-export-import
# MAGIC pip install git+https:///github.com/mlflow/mlflow-export-import/#egg=mlflow-export-import

# COMMAND ----------

# MAGIC %run ./credentials

# COMMAND ----------

# MAGIC %md ## Setup
# MAGIC Make sure the mount to the target s3 bucket is set up. See the **mount** notebook in this directory

# COMMAND ----------

# DBTITLE 1,variables
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
 
logfile = f"export_models_{date}.log"
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
# MAGIC # echo $DATABRICKS_HOST
# MAGIC # echo $DATABRICKS_TOKEN

# COMMAND ----------

# DBTITLE 0,`export-models` options
# MAGIC %sh 
# MAGIC export-models --help

# COMMAND ----------

# MAGIC %md ## Execute

# COMMAND ----------

# DBTITLE 1,cli execution
# MAGIC %sh 
# MAGIC export-models \
# MAGIC   --output-dir /dbfs/mnt/aws-ds-non-prod/mlflow-migration-models \
# MAGIC   --models all \
# MAGIC   # --stages 'Production,Staging,Archived,None' \
# MAGIC   --export-permissions True \
# MAGIC   --notebook-formats SOURCE \
# MAGIC   --export-version-model True \
# MAGIC   --use-threads True

# COMMAND ----------


