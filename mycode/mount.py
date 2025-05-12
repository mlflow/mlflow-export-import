# Databricks notebook source
# MAGIC %md 
# MAGIC I added the AWS keys to Databricks secrets using the databricks cli. For Azure DEV, the profile name is **azure-dev**. 
# MAGIC
# MAGIC Raj had to give me the AWS keys because I don't have permission to create  AWS IAM users with S3 access. 
# MAGIC
# MAGIC ### Reference
# MAGIC - https://docs.databricks.com/aws/en/dbfs/mounts#mount-a-bucket-using-aws-keys
# MAGIC - https://docs.databricks.com/aws/en/security/secrets#create-a-secret-scope
# MAGIC - https://docs.databricks.com/aws/en/security/secrets#create-a-secret

# COMMAND ----------

# DBTITLE 1,s3 bucket in ds-non-prod
access_key = dbutils.secrets.get(scope = "aws", key = "aws-access-key")
secret_key = dbutils.secrets.get(scope = "aws", key = "aws-secret-key")
encoded_secret_key = secret_key.replace("/", "%2F")
aws_bucket_name = "s3-us-east-2-dev-ds-non-prod-s3-app-ovisg"
mount_name = "aws-ds-non-prod"

dbutils.fs.mount(f"s3a://{access_key}:{encoded_secret_key}@{aws_bucket_name}", f"/mnt/{mount_name}")
display(dbutils.fs.ls(f"/mnt/{mount_name}"))



