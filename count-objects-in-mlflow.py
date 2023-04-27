# Databricks notebook source
import mlflow
import pandas as pd
import numpy as np

# COMMAND ----------

# DBTITLE 1,inspection functions
def exp_id(exp):
  try:
    return exp.experiment_id
  except:
    return "none"
  
def exp_id_after_import(exp):
  try:
    return exp.experiment_id
  except:
    return "none"

def email(exp):
  try:
    return exp.tags['mlflow.ownerEmail']
  except:
    return "none"
  
def n_runs(exp):
  try:
    return len(mlflow.search_runs(exp.experiment_id, run_view_type=3))
  except:
    0

# COMMAND ----------

data = np.array([(exp_id(exp), n_runs(exp), email(exp)) for exp in mlflow.search_experiments(view_type=3)])

df = pd.DataFrame(dict(experiment_id=data[:,0], n_runs=data[:,1], owner_email=data[:,2]))
df["n_runs"] = df.n_runs.astype(int)

print("There are", df.shape[0], "total experiments")
print("There are", df.query("n_runs > 0").shape[0], "experiments with at least one run")
print("There are", df.query("n_runs == 0").shape[0], "experiments with no runs")
print("There are", df.n_runs.sum(), "runs")
print("There are", len(mlflow.search_registered_models()), "registered models")
