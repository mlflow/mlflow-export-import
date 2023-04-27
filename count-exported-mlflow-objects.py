# Databricks notebook source
import re
import pandas as pd
import numpy as np

# COMMAND ----------

# MAGIC %md ## Experiments

# COMMAND ----------

# MAGIC %sh 
# MAGIC find /dbfs/mnt/ccidsdatascidatalake/mlflow-migration/experiments/experiments -type d -maxdepth 2 > exported_experiments

# COMMAND ----------

exp_pat = "^.*\/dbfs\/mnt\/ccidsdatascidatalake\/mlflow-migration\/experiments\/experiments\/(.*)$"

filepath = "exported_experiments"
capture = [re.findall(exp_pat, line) for line in open(filepath)]

# COMMAND ----------

def parse_exp_run(s):
  res = s.split("/")
  return res if len(res)==2 else [*res,None]

parsed = np.array([parse_exp_run(c[0]) for c in capture if c])

df_parsed = pd.DataFrame(dict(experiment_id=parsed[:,0], run_id=parsed[:,1]))

exp_df = df_parsed.groupby("experiment_id").run_id.count().to_frame()
exp_df.columns = ["n_runs"]

# COMMAND ----------

# MAGIC %md ## Models

# COMMAND ----------

# MAGIC %sh 
# MAGIC ls /dbfs/mnt/ccidsdatascidatalake/mlflow-migration/experiments/models/ > exported_models

# COMMAND ----------

with open("exported_models") as f:
  n_models = len(f.readlines())

# COMMAND ----------

# MAGIC %md ## Report

# COMMAND ----------

print("There are", exp_df.shape[0], "total experiments")
print("There are", exp_df.query("n_runs > 0").shape[0], "experiments with at least one run")
print("There are", exp_df.query("n_runs == 0").shape[0], "experiments with no runs")
print("There are", exp_df.n_runs.sum(), "runs")
print("There are", n_models, "registered models")

# COMMAND ----------


