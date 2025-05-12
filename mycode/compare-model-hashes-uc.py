# Databricks notebook source
# DBTITLE 1,azure model hashes
with open("azure-model-hashes", "r") as f:
  lines = f.readlines()

az_model_hashes = dict()
for line in lines:
  k, v = line.lower().strip("\n").split(": ")
  if v=="model file not found":
    v=None
  az_model_hashes[k] = v

# COMMAND ----------

# DBTITLE 1,aws model hashes
with open("aws-model-hashes-uc", "r") as f:
  lines = f.readlines()

aws_model_hashes = dict()
for line in lines:
  k, v = line.lower().replace("ds_nonprod.migrated_models.","").strip("\n").split(": ")
  if v=='model not found': 
    v=None
  aws_model_hashes[k] = v

# COMMAND ----------

aws_model_hashes

# COMMAND ----------

# DBTITLE 1,num registered models on each platform
len(az_model_hashes), len(aws_model_hashes)

# COMMAND ----------

# DBTITLE 1,missing models
set(az_model_hashes.keys()) - set(aws_model_hashes.keys()), set(aws_model_hashes.keys()) - set(az_model_hashes.keys()) 

# COMMAND ----------

import pandas as pd

azure_df = pd.DataFrame(az_model_hashes, index=["azure"])
aws_df = pd.DataFrame(aws_model_hashes, index=["aws"])
model_hashes_pdf = pd.concat((azure_df, aws_df)).T

model_hashes_pdf["match"] = model_hashes_pdf.azure == model_hashes_pdf.aws

model_hashes = spark.createDataFrame(model_hashes_pdf.reset_index())

display(model_hashes)

# COMMAND ----------

display(model_hashes.where("not match and azure is not null and aws is not null"))

# COMMAND ----------


