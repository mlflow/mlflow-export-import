# Databricks notebook source
# MAGIC %md ### README - MLflow Export/Import
# MAGIC 
# MAGIC #### Overview
# MAGIC * Export and import MLflow objects - runs, experiments or registered models.
# MAGIC * Copy MLflow objects from one workspace (tracking server) to another.
# MAGIC * Customers often need to copy objects (e.g. experiments) to another workspace.
# MAGIC   * For example, we train model runs in the dev workspace, and then we wish to promote the best run to a prod workspace.
# MAGIC   * Can't do this today.
# MAGIC   * Customer experiment data is currently locked into a workspace and not portable.
# MAGIC * These notebooks are an unofficial tool that address this problem.
# MAGIC * You will need to set up a common cloud bucket mounted on DBFS in your source and destination workspaces.
# MAGIC * For details see:
# MAGIC   * [MLflow Export Import](https://databricks.atlassian.net/wiki/spaces/UN/pages/800754006/MLflow+Export+Import) - wiki page
# MAGIC   * Github code:
# MAGIC     * Source code: https://github.com/amesar/mlflow-export-import
# MAGIC     * Databricks notebooks: https://github.com/amesar/mlflow-export-import/tree/master/databricks_notebooks
# MAGIC   
# MAGIC #### Architecture
# MAGIC 
# MAGIC <img src="https://github.com/amesar/mlflow-export-import/blob/master/architecture.png?raw=true"  width="700" />
# MAGIC 
# MAGIC #### Notebooks
# MAGIC 
# MAGIC ##### Bulk Notebooks
# MAGIC * [Export_Experiments]($./bulk/Export_Experiments) - export experiments to folder
# MAGIC * [Export_Models]($./bulk/Export_Models) - export experiments to folder
# MAGIC 
# MAGIC ##### Point Notebooks
# MAGIC * Run
# MAGIC   * [Export_Run]($./Export_Run) - export run to folder
# MAGIC   * [Import_Run]($./Import_Run) - import run from folder
# MAGIC * Experiment
# MAGIC   * [Export_Experiment]($./Export_Experiment) - export an experiment (and all its runs) to folder
# MAGIC     * [Export_Experiment_List]($./Export_Experiment_List) - export a list of experiments (or all) to folder - WIP
# MAGIC   * [Import_Experiment]($./Import_Experiment) - import experiment from folder
# MAGIC * Registered Model
# MAGIC   * [Export_Model]($./Export_Model) - export model (and runs of all its versions) to folder
# MAGIC   * [Import_Model]($./Import_Model) - import model from folder
# MAGIC * [Common]($./Common)
# MAGIC   
# MAGIC #### Limitations
# MAGIC 
# MAGIC * The OSS export/import logic is solid.
# MAGIC * Databricks limitations:
# MAGIC   * We cannot export the notebook revision linked to a run since the Databricks workspace API does not support exporting/importing notebook revisions.
# MAGIC   * As a convenience, when a run is exported the notebook (current revision) is exported. It is not attached to any run.
# MAGIC   * When importing a run you will have a dead notebook revision ID link.
# MAGIC 
# MAGIC #### Setup
# MAGIC 
# MAGIC There are two different ways to install the package.
# MAGIC 
# MAGIC ##### Install package in notebook
# MAGIC 
# MAGIC This is the default executed in the [Common]($./Common) notebook.
# MAGIC 
# MAGIC [Install notebook-scoped libraries with %pip](https://docs.databricks.com/libraries/notebooks-python-libraries.html#install-notebook-scoped-libraries-with-pip).
# MAGIC 
# MAGIC ```
# MAGIC pip install git+https:///github.com/amesar/mlflow-export-import/#egg=mlflow-export-import
# MAGIC ```
# MAGIC 
# MAGIC ##### Install package as a wheel on cluster 
# MAGIC 
# MAGIC Build the wheel artifact on your laptop, upload it to DBFS and then [install it on your cluster](https://docs.databricks.com/libraries/cluster-libraries.html).
# MAGIC 
# MAGIC ```
# MAGIC python setup.py bdist_wheel
# MAGIC databricks fs cp dist/mlflow_export_import-1.0.0-py3-none-any.whl {MY_DBFS_PATH}
# MAGIC ```
# MAGIC 
# MAGIC Note, on the demo shard the wheel can be found at: `dbfs:/home/andre.mesarovic@databricks.com/lib/wheels/mlflow_export_import-1.0.0-py3-none-any.whl`

# COMMAND ----------

# MAGIC %md Last updated: 2022-08-11