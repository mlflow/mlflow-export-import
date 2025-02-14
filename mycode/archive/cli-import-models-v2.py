# Databricks notebook source
# MAGIC %md ### Manually loop over models instead of using `import-models`, which is unreliable
# MAGIC
# MAGIC TODO: needs work with model and experiment names

# COMMAND ----------

# DBTITLE 1,install latest pkg from github
# MAGIC %sh 
# MAGIC #pip install mlflow-export-import
# MAGIC pip install git+https:///github.com/mlflow/mlflow-export-import/#egg=mlflow-export-import

# COMMAND ----------

# DBTITLE 1,we can see the s3 mount from %sh :)
# MAGIC %sh ls /dbfs/mnt/ccidsdatascidatalake/

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

with open("/dbfs/FileStore/shared_uploads/darrell.coles@crowncastle.com/aws_databricks_credentials") as f:
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
# MAGIC import-model --help

# COMMAND ----------

# DBTITLE 1,make model-experiment file
import json

input_dir = "/dbfs/mnt/ccidsdatascidatalake/mlflow-migration-models/models" 

def get_most_recent_experiment_name(model):
  try:
    newest = max(model["mlflow"]["registered_model"]["versions"], key=lambda v:v["last_updated_timestamp"])
    return newest["_experiment_name"]
  except:
    return None

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

# DBTITLE 1,cli execution
# MAGIC %sh 
# MAGIC
# MAGIC input_dir=/dbfs/mnt/ccidsdatascidatalake/mlflow-migration-models/models
# MAGIC
# MAGIC while IFS=, read model experiment; 
# MAGIC do 
# MAGIC   import-model \
# MAGIC     --input-dir '$input_dir/$model' \
# MAGIC     --model '$model' \
# MAGIC     --experiment-name '$experiment' \
# MAGIC     --delete-model True \
# MAGIC     --import-source-tags True \
# MAGIC     --verbose True;
# MAGIC done < model_experiment

# COMMAND ----------


