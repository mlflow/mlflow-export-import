# Databricks notebook source
# MAGIC %md ## MLflow Export Import - Single Notebooks
# MAGIC 
# MAGIC * Transitively export an MLflow object and specify its destination object name.
# MAGIC * By transitively we mean export other linked objects to maintain referential integrity and reproducibility. 
# MAGIC * For example, when we export a registered model we also export the runs its versions are linked to and also the experiment that the runs belong to.
# MAGIC 
# MAGIC **Notebooks**
# MAGIC * Run
# MAGIC   * [Export_Run]($./Export_Run)  
# MAGIC   * [Import_Run]($./Import_Run)
# MAGIC * Experiment
# MAGIC   * [Export_Experiment]($./Export_Experiment) - export an experiment and its runs (run.info, run.data and artifacts).
# MAGIC   * [Import_Experiment]($./Import_Experiment)
# MAGIC * Registered Model
# MAGIC   * [Export_Model]($./Export_Model) - export a model, its versions and their runs.
# MAGIC   * [Import_Model]($./Import_Model)
# MAGIC * [Common]($./Common)
# MAGIC 
# MAGIC **More information**
# MAGIC 
# MAGIC See [github.com/mlflow/mlflow-export-import/blob/master/README_single.md](https://github.com/mlflow/mlflow-export-import/blob/master/README_single.md).

# COMMAND ----------

# MAGIC %md Last updated: 2023-03-08
