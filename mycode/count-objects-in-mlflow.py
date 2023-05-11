# Databricks notebook source
import mlflow
import pandas as pd
import numpy as np
from datetime import datetime

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
    
def run_start_time(run: pandas.Series)->datetime.datetime:
  return datetime(
    year=run.start_time.year,
    month=run.start_time.month,
    day=run.start_time.day)
  
def n_runs(exp, start_time=None):
  """
  Parameters
  ==========
  start_time (str): date; format 'YYYY-MM-DD'  
  """
  runs = mlflow.search_runs(exp.experiment_id)
  try:
    if start_time:
      year, month, day = start_time.split("-")
      dt_thresh = datetime(year=int(year), month=int(month), day=int(day))
      return len([1 for _, run in runs.iterrows() if run_start_time(run) >= dt_thresh])
    else:
      return len(runs)
  except:
    0

# COMMAND ----------

start_time = "2022-11-01"

data = np.array([(exp_id(exp), n_runs(exp, start_time), email(exp)) for exp in mlflow.search_experiments()])

df = pd.DataFrame(dict(experiment_id=data[:,0], n_runs=data[:,1], owner_email=data[:,2]))
df["n_runs"] = df.n_runs.astype(int)

print("There are", df.shape[0], "total experiments")
print("There are", df.query("n_runs > 0").shape[0], "experiments with at least one run")
print("There are", df.query("n_runs == 0").shape[0], "experiments with no runs")
print("There are", df.n_runs.sum(), "runs")
print("There are", len(mlflow.search_registered_models()), "registered models")

# COMMAND ----------


