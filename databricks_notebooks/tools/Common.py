# Databricks notebook source
# MAGIC %pip install -U mlflow-skinny
# MAGIC %pip install -U git+https:///github.com/mlflow/mlflow-export-import/#egg=mlflow-export-import
# MAGIC dbutils.library.restartPython()

# COMMAND ----------

import json
def dump_json(dct,title=""):
    print(json.dumps(dct, indent=2))
    if title:
        print(f"{title}:")

# COMMAND ----------

def is_unity_catalog_model(model_name):
    return "." in model_name
    
def split_model_uri(model_uri):
    toks = model_uri.split("/")
    return toks[1], toks[2]

# COMMAND ----------

import mlflow

def set_registry_uri(model_name):
    if model_name.startswith("models:/"):
        model_name = split_model_uri(model_name)[0]
    if is_unity_catalog_model(model_name):
        mlflow.set_registry_uri("databricks-uc")
    else:
        mlflow.set_registry_uri("databricks")
    print("mlflow.registry_uri:", mlflow.get_registry_uri())

# COMMAND ----------

def to_json_signature(signature):
    def _normalize(lst):
        import json
        return json.loads(lst) if lst else lst
    return { k:_normalize(v) for k,v in signature.items()}

# COMMAND ----------

def assert_widget(value, name):
    if len(value.rstrip())==0:
        raise RuntimeError(f"ERROR: '{name}' widget is required")
