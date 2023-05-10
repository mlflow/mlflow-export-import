# Databricks notebook source
import mlflow
mlflow.__version__

# COMMAND ----------

for exp in mlflow.search_experiments():
  eid = exp.experiment_id
  mlflow.delete_experiment(experiment_id=eid)
