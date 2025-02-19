# Databricks notebook source
# DBTITLE 1,azure model hashes
with open("azure-model-hashes", "r") as f:
  lines = f.readlines()

az_model_hashes = dict()
for line in lines:
  k, v = line.strip("\n").split(": ")
  az_model_hashes[k] = v

# COMMAND ----------

# DBTITLE 1,aws model hashes
with open("aws-model-hashes", "r") as f:
  lines = f.readlines()

aws_model_hashes = dict()
for line in lines:
  k, v = line.strip("\n").split(": ")
  aws_model_hashes[k] = v

# COMMAND ----------

# DBTITLE 1,num registered models on each platform
len(az_model_hashes), len(aws_model_hashes)

# COMMAND ----------

# DBTITLE 1,missing models
set(az_model_hashes.keys()) - set(aws_model_hashes.keys()), set(aws_model_hashes.keys()) - set(az_model_hashes.keys()) 

# COMMAND ----------

for k, v in az_model_hashes.items():
  try:
    if v != aws_model_hashes[k]:
      print(k, v, aws_model_hashes[k],"\n")
  except:
    print(k, "is not in the AWS model set\n")

# COMMAND ----------


