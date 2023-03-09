# Databricks notebook source
# MAGIC %md ### Scratch

# COMMAND ----------

base_dir="/dbfs/home/andre.mesarovic@databricks.com/mlflow_export_import"
import os
os.environ["BASE_DIR"] = base_dir
os.environ["SINGLE_DIR"] = os.path.join(base_dir,"single")
os.environ["BULK_DIR"] = os.path.join(base_dir,"bulk")
base_dir

# COMMAND ----------

# MAGIC %sh 
# MAGIC ls $BASE_DIR

# COMMAND ----------

# MAGIC %sh ls $SINGLE_DIR/experiments

# COMMAND ----------

# MAGIC %sh ls $SINGLE_DIR/models

# COMMAND ----------

# MAGIC %md #### Create export directories

# COMMAND ----------

# MAGIC %sh 
# MAGIC BASE_DIR=/dbfs/home/andre.mesarovic@databricks.com/mlflow_export_import
# MAGIC 
# MAGIC mkdir -p $BASE_DIR/single/runs
# MAGIC mkdir -p $BASE_DIR/single/experiments
# MAGIC mkdir -p $BASE_DIR/single/models
# MAGIC 
# MAGIC mkdir -p $BASE_DIR/bulk/experiments
# MAGIC mkdir -p $BASE_DIR/bulk/models
# MAGIC mkdir -p $BASE_DIR/bulk/all

# COMMAND ----------

# MAGIC %md ## Models

# COMMAND ----------

# MAGIC %sh
# MAGIC cd $SINGLE_DIR/models/andre_02a_Sklearn_Train_Predict
# MAGIC ls -l

# COMMAND ----------

# MAGIC %sh cd $SINGLE_DIR/models/andre_02a_Sklearn_Train_Predict
# MAGIC cat model.json

# COMMAND ----------

# MAGIC %md ## Experiments#

# COMMAND ----------

# MAGIC %sh ls -l $SINGLE_DIR/experiments

# COMMAND ----------

# MAGIC %sh ls -l $SINGLE_DIR/experiments/782312627266391

# COMMAND ----------

# MAGIC %cat $SINGLE_DIR/experiments/782312627266391/experiment.json

# COMMAND ----------

# MAGIC %md ### Runs

# COMMAND ----------

# MAGIC %sh
# MAGIC cd $SINGLE_DIR/runs
# MAGIC ls -l

# COMMAND ----------

# MAGIC %sh
# MAGIC cd $SINGLE_DIR/runs/b81506f3f16b46079cfe4e59265239b7
# MAGIC ls -l

# COMMAND ----------

# MAGIC %sh
# MAGIC cd $SINGLE_DIR/runs/b81506f3f16b46079cfe4e59265239b7
# MAGIC cat run.json

# COMMAND ----------

# MAGIC %md ## Explode - Misc

# COMMAND ----------

path=/dbfs/home/andre.mesarovic@databricks.com/lib/wheels/mlflow_export_import-1.2.0-py3-none-any.whl

# COMMAND ----------

# MAGIC %sh whl=/dbfs/home/andre.mesarovic@databricks.com/lib/wheels/mlflow_export_import-1.2.0-py3-none-any.whl
# MAGIC 
# MAGIC ls -l $whl
# MAGIC #mkdir /tmp/foo
# MAGIC cd /tmp/foo
# MAGIC echo "PWD: $PWD"
# MAGIC ls -l 
# MAGIC unzip $whl
# MAGIC ls -l 

# COMMAND ----------

# MAGIC %sh
# MAGIC cd /tmp/foo
# MAGIC ls -l

# COMMAND ----------

# MAGIC %sh 
# MAGIC cd /tmp/foo
# MAGIC cat mlflow_export_import/experiment/export_experiment.py 
