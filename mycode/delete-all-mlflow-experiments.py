# Databricks notebook source
import mlflow
mlflow.__version__

# COMMAND ----------

for exp in mlflow.search_experiments():
  eid = exp.experiment_id
  try:
    mlflow.delete_experiment(experiment_id=eid)
  except:
    print(f"Experiment {eid} not deleted")

# COMMAND ----------

mlflow.search_experiments()

# COMMAND ----------


