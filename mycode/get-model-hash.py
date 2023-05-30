# Databricks notebook source
# MAGIC %md
# MAGIC This notebook takes the name of a registered mlflow model and hashes its production stage.
# MAGIC
# MAGIC Because MLflow artifacts are abstracted behind a permission wall, the notebook first uses `mlflow-export-import` to export the production model to ephemeral storage (public blobs).
# MAGIC Once the model is exported, the notebook finds the first production model (technically, there should only be one but this may not be the case in DEV) and hashes its model files, which are stored in the `model/` subdirectory.
# MAGIC The model files are `conda.yaml`, `MLmodel`, `model.pkl`, and `requirements.txt`.
# MAGIC The 4 hashes are then concatenated and hashed to create the final, model hash.

# COMMAND ----------

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

model_dir = f"/mnt/public-blobs/dcoles/mlflow-migration-validation/{model_name}"

# COMMAND ----------

# DBTITLE 1,set env vars
import os 
from datetime import datetime
import pytz

os.environ["MLFLOW_EXPORT_IMPORT_LOG_FORMAT"]="%(threadName)s-%(levelname)s-%(message)s"

os.environ["MLFLOW_TRACKING_URI"]="databricks"

os.environ["MLFLOW_MODEL_NAME"]=model_name

# NEED FOR THE CLI CALL
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

# DBTITLE 1,export prod stage for hashing
# MAGIC %sh 
# MAGIC export-model \
# MAGIC   --model "$MLFLOW_MODEL_NAME"\
# MAGIC   --output-dir /dbfs/mnt/public-blobs/dcoles/mlflow-migration-validation/"$MLFLOW_MODEL_NAME" \
# MAGIC   --stages 'Production' \
# MAGIC   --notebook-formats SOURCE

# COMMAND ----------

# DBTITLE 1,hash model directory
from hashlib import md5 

def hash(path: str):
  with open(path,"rb") as f:
    return md5(f.read()).hexdigest()
  
def get_dir_content(ls_path):
  dir_paths = dbutils.fs.ls(ls_path)
  subdir_paths = [get_dir_content(p.path) for p in dir_paths if p.isDir() and p.path != ls_path]
  flat_subdir_paths = [p for subdir in subdir_paths for p in subdir]
  return list(map(lambda p: p.path, dir_paths)) + flat_subdir_paths
   
# only get specific file paths
rget_dir_filenames = lambda ls_path: [p for p in get_dir_content(ls_path) if p.endswith(("MLmodel", "conda.yaml", "model.pkl", "requirements.txt"))]

try:
  # recursively get all file paths in model directory 
  filepaths = rget_dir_filenames(model_dir)

  # hash each file
  hashes = list()
  for path in filepaths:
    hashes.append(hash(path.replace("dbfs:", "/dbfs")))
  
  # sort hashes to guarantee repeatability 
  hashes = sorted(hashes)

  # concatenate sorted hashes
  exec(f"bhashes = b'{''.join(hashes)}'")

  # hash the concatenated hashes
  result = f"{model_name}: {md5(bhashes).hexdigest()}"

except:
  result = f"{model_name}: No Production stages found"

# COMMAND ----------

dbutils.notebook.exit(result)

# COMMAND ----------


