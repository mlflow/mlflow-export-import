# Databricks notebook source
# MAGIC %md ### MLflow Export Import - Databricks Notebooks
# MAGIC 
# MAGIC #### Overview
# MAGIC * Copy MLflow objects (runs, experiments or registered models) between MLflow workspaces (tracking server).
# MAGIC * Customers often need to copy MLflow objects to another workspace.
# MAGIC   * For example, we train model runs in the dev workspace, and then we wish to promote the best run to a prod workspace.
# MAGIC   * No out-of-the-box way to do this today.
# MAGIC   * Customer MLflow object data is currently locked into a workspace and not portable.
# MAGIC * In order to copy MLflow objects between workspaces, you will need to set up a shared cloud bucket mounted on each workspace's DBFS.
# MAGIC 
# MAGIC #### Details
# MAGIC 
# MAGIC * [MLflow Export Import](https://databricks.atlassian.net/wiki/spaces/UN/pages/800754006/MLflow+Export+Import) - Internal Databricks wiki page.
# MAGIC * Github:
# MAGIC   * [README](https://github.com/mlflow/mlflow-export-import/blob/master/README.md)
# MAGIC   * Source code: https://github.com/mlflow/mlflow-export-import - source of truth with extensive documentation.
# MAGIC   * Databricks notebooks: https://github.com/mlflow/mlflow-export-import/tree/master/databricks_notebooks.
# MAGIC   
# MAGIC #### Architecture
# MAGIC 
# MAGIC <img src="https://github.com/amesar/mlflow-export-import/blob/master/architecture.png?raw=true"  width="700" />
# MAGIC 
# MAGIC #### Notebooks 
# MAGIC 
# MAGIC * [Single notebooks]($single/_README) - Copy one MLflow object and control its destination object name.
# MAGIC * [Bulk notebooks]($bulk/_README) - Copy multiple MLflow objects. The target object name will be the same as the source object name.
# MAGIC 
# MAGIC #### Limitations
# MAGIC 
# MAGIC * [General limitations](https://github.com/mlflow/mlflow-export-import/blob/master/README_limitations.md#general-limitations).
# MAGIC * [Databricks limitations](https://github.com/mlflow/mlflow-export-import/blob/master/README_limitations.md#databricks-limitations).
# MAGIC 
# MAGIC #### Setup
# MAGIC 
# MAGIC Use [notebook scoped libraries](https://docs.databricks.com/libraries/notebooks-python-libraries.html#install-notebook-scoped-libraries-with-pip) to install the [mlflow-export-import](https://pypi.org/project/mlflow-export-import) library in your notebook.
# MAGIC 
# MAGIC **Install from PyPI**
# MAGIC ```
# MAGIC pip install mlflow-export-import
# MAGIC ```
# MAGIC 
# MAGIC **Install from github**
# MAGIC 
# MAGIC ```
# MAGIC pip install git+https:///github.com/amesar/mlflow-export-import/#egg=mlflow-export-import
# MAGIC ```

# COMMAND ----------

# MAGIC %md Last updated: 2023-01-19