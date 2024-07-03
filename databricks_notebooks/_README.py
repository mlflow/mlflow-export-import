# Databricks notebook source
# MAGIC %md ### MLflow Export Import - Databricks Notebooks
# MAGIC
# MAGIC #### Overview
# MAGIC * Copy MLflow objects (runs, experiments or registered models) either in the same workspace or to another workspace.
# MAGIC * Supports both classical Workspace Registry and newer Unity Catalog Registry.
# MAGIC * Customers often need to copy MLflow objects to another workspace.
# MAGIC   * For example, we train model runs in the dev workspace, and then we wish to promote the best run to a prod workspace.
# MAGIC   * No out-of-the-box way to do this today.
# MAGIC   * Customer MLflow object data is currently locked into a workspace and not portable.
# MAGIC * In order to copy MLflow objects between workspaces, you need to use a shared cloud storage location:
# MAGIC   * DBFS: Create a [DBFS mount point](https://docs.databricks.com/en/dbfs/mounts.html) on both workspaces pointing to the shared location.
# MAGIC     * Example: `dbfs:/mnt/mlflow_export_import/single/experiments`
# MAGIC   * Unity Catalog: use a volume shared by both workspaces using the same Unity Catalog metastore.
# MAGIC     * Example: `/Volumes/my_catalog/my_schema/mlflow_export_import_volume/single/experiments`
# MAGIC
# MAGIC #### Details
# MAGIC
# MAGIC * [README](https://github.com/mlflow/mlflow-export-import/blob/master/README.md)
# MAGIC * Source code: https://github.com/mlflow/mlflow-export-import - source of truth with extensive documentation.
# MAGIC * Databricks notebooks: https://github.com/mlflow/mlflow-export-import/tree/master/databricks_notebooks.
# MAGIC   
# MAGIC #### Architecture
# MAGIC
# MAGIC <img src="https://github.com/mlflow/mlflow-export-import/blob/issue-138-copy-model-version/diagrams/architecture.png?raw=true"  width="700" />
# MAGIC
# MAGIC #### Notebooks 
# MAGIC
# MAGIC ##### Notebooks
# MAGIC * [Single notebooks]($single/_README) - Copy one MLflow object from one tracking server (workspace) to another.
# MAGIC * [Bulk notebooks]($bulk/_README) - Copy multiple MLflow objects. The target object name will be the same as the source object name.
# MAGIC * [Copy notebooks]($copy/_README) - Directly copy a model version or run using a temp directory as intermediate instead of an explicit intermediate storage location.
# MAGIC * [Tools notebooks]($tools/_README) - Additional tools such as model signature notebooks.
# MAGIC
# MAGIC #### Limitations
# MAGIC
# MAGIC * [General limitations](https://github.com/mlflow/mlflow-export-import/blob/master/README_limitations.md#general-limitations)
# MAGIC * [Databricks limitations](https://github.com/mlflow/mlflow-export-import/blob/master/README_limitations.md#databricks-limitations)
# MAGIC
# MAGIC #### Experimental
# MAGIC
# MAGIC ##### [Console Script]($scripts/_README) notebooks
# MAGIC * Command-line scripts using the Linux shell (%sh).
# MAGIC * [Console_Scripts]($scripts/Console_Scripts) 
# MAGIC
# MAGIC #### Databricks internal
# MAGIC * [MLflow Export Import](https://databricks.atlassian.net/wiki/spaces/UN/pages/800754006/MLflow+Export+Import) - Wiki page.
# MAGIC
# MAGIC ##### Last updated: _2024-07-03_
