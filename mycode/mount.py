# Databricks notebook source
# MAGIC %md 
# MAGIC I added the AWS keys to Databricks secrets using the databricks cli. For Azure DEV, the profile name is **azure-dev** 

# COMMAND ----------

# DBTITLE 1,s3 bucket in ds-non-prod
access_key = dbutils.secrets.get(scope = "aws", key = "aws-access-key")
secret_key = dbutils.secrets.get(scope = "aws", key = "aws-secret-key")
encoded_secret_key = secret_key.replace("/", "%2F")
aws_bucket_name = "s3-us-east-2-dev-ds-non-prod-s3-app-ovisg"
mount_name = "aws-ds-non-prod"

dbutils.fs.mount(f"s3a://{access_key}:{encoded_secret_key}@{aws_bucket_name}", f"/mnt/{mount_name}")
display(dbutils.fs.ls(f"/mnt/{mount_name}"))

# COMMAND ----------


