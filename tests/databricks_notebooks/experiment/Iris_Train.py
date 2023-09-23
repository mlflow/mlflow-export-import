# Databricks notebook source
# MAGIC %md ## Iris Train
# MAGIC * Train and register a model for testing purposes.

# COMMAND ----------

dbutils.widgets.text("Experiment", "")
experiment_name = dbutils.widgets.get("Experiment")

dbutils.widgets.text("Registered model", "")
registered_model = dbutils.widgets.get("Registered model")
if registered_model == "": registered_model = None 

experiment_name, registered_model

# COMMAND ----------

import mlflow
if experiment_name:
    mlflow.set_experiment(experiment_name)

# COMMAND ----------

from sklearn import svm, datasets
print("mlflow.version:", mlflow.__version__)

with mlflow.start_run() as run:
    print("run_id:",run.info.run_id)
    print("experiment_id:",run.info.experiment_id)
    iris = datasets.load_iris()
    mlflow.log_metric("degree", 5)
    model = svm.SVC(C=2.0, degree=5, kernel="rbf")
    model.fit(iris.data, iris.target)
    mlflow.sklearn.log_model(model, "model", registered_model_name=registered_model)
