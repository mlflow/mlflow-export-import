# Databricks notebook source
# MAGIC %md ### README - MLflow Export/Import
# MAGIC 
# MAGIC #### Overview
# MAGIC * Export and import MLflow objects - runs, experiments or registered models.
# MAGIC * Copy MLflow objects from one workspace (tracking server) to another.
# MAGIC * Customers often need to copy MLflow objects (registered models, experiments or runs) to another workspace.
# MAGIC   * For example, we train model runs in the dev workspace, and then we wish to promote the best run to a production workspace.
# MAGIC   * There is no official and easy way to do this.
# MAGIC   * Customer experiment data is currently locked into a workspace and not portable.
# MAGIC * These notebooks invoke the [mlflow-export-import](https://github.com/mlflow/mlflow-export-import) package to address these problems.
# MAGIC * You will need to set up a shared cloud bucket mounted on DBFS in your source and destination workspaces.
# MAGIC * For details see:
# MAGIC   * [MLflow Export Import](https://databricks.atlassian.net/wiki/spaces/UN/pages/800754006/MLflow+Export+Import) - Databricks wiki page
# MAGIC   * Github code:
# MAGIC     * Source code: https://github.com/mlflow/mlflow-export-import
# MAGIC     * Databricks notebooks: https://github.com/mlflow/mlflow-export-import/tree/master/databricks_notebooks
# MAGIC   
# MAGIC #### Architecture
# MAGIC 
# MAGIC <img src="https://github.com/mlflow/mlflow-export-import/blob/master/architecture.png?raw=true"  width="700" />
# MAGIC 
# MAGIC #### Notebooks
# MAGIC * Run
# MAGIC   * [Export_Run]($./Export_Run) - export run to folder
# MAGIC   * [Import_Run]($./Import_Run) - import run from folder
# MAGIC * Experiment
# MAGIC   * [Export_Experiment]($./Export_Experiment) - export an experiment (and all its runs) to folder
# MAGIC   * [Import_Experiment]($./Import_Experiment) - import experiment from folder
# MAGIC * Registered Model
# MAGIC   * [Export_Model]($./Export_Model) - export model (and runs of all its versions) to folder
# MAGIC   * [Import_Model]($./Import_Model) - import model from folder
# MAGIC * [Common]($./Common)
# MAGIC   
# MAGIC #### Limitations
# MAGIC 
# MAGIC * [General limitations](https://github.com/mlflow/mlflow-export-import#general-limitations)
# MAGIC * [Databricks limitations](https://github.com/mlflow/mlflow-export-import#databricks-limitations)
# MAGIC 
# MAGIC #### Setup
# MAGIC 
# MAGIC 
# MAGIC The [Common]($./Common) notebook installs the mlflow-export-import package from github.
# MAGIC 
# MAGIC ```
# MAGIC pip install git+mlflo`https:///github.com/mlflow/mlflow-export-import/#egg=mlflow-export-import
# MAGIC ```
# MAGIC 
# MAGIC For Databricks documentation see: [Install notebook-scoped libraries with %pip](https://docs.databricks.com/libraries/notebooks-python-libraries.html#install-notebook-scoped-libraries-with-pip).

# COMMAND ----------

# MAGIC %md Last updated: 2022-06-27