# Databricks notebook source
def get_credentials_path(platform):
  
  az_creds_path = "/dbfs/FileStore/shared_uploads/darrell.coles@crowncastle.com/azure_databricks_credentials"
  aws_creds_path = "/Workspace/Users/darrell.coles@crowncastle.com/aws_databricks_credentials"

  match platform:
    case "": raise ValueError("platform must be specified")
    case "azure": return az_creds_path
    case "aws": return aws_creds_path
