# Databricks notebook source
# MAGIC %md ### Export Registered Model
# MAGIC
# MAGIC ##### Overview
# MAGIC * Export a registered model and all the runs associated with its latest versions to a DBFS folder.
# MAGIC * Output file `model.json` contains exported model metadata.
# MAGIC * Each run and its artifacts are stored as a sub-directory.
# MAGIC
# MAGIC ##### Parameters
# MAGIC * `1. Model` - Registered model name to export.
# MAGIC * `2. Output base directory` - Base output directory to which the model name will be appended to.
# MAGIC * `3. Stages` - Model version stages to export.
# MAGIC * `4. Export latest versions`.
# MAGIC * `5. Versions` - Comma delimited version numbers to export.
# MAGIC * `6. Export permissions` - Export Databricks permissions.
# MAGIC * `7. Export version MLflow model`.
# MAGIC * `8. Notebook formats` - Notebook formats to export.

# COMMAND ----------

# MAGIC %md ### Include setup

# COMMAND ----------

# MAGIC %run ./Common

# COMMAND ----------

from Configs import *
from mlflow_export_import.model.export_model import export_model

Configs.EXPORT_START_DATE = '2024-02-16'
Configs.EXPORT_END_DATE = '2024-02-21'
Configs.APPLY_EXPORT_FILTER = True
Configs.SKIP_EXPORT_IF_EXISTS = True

output_root = '/dbfs/mnt/devadlstoragesnoxto01/migration/MLFlow'
stages = ['None'] # ['None', 'Staging', 'Production', 'Archived']
export_version_model = True
export_permissions = False
export_latest_versions = False
notebook_formats = ['SOURCE']
versions = []

Configs.EXPORT_MODEL_NAMES = ['qw_model_train_ESD_live']

# COMMAND ----------

# MAGIC %md ### Export the models

# COMMAND ----------

for model_name in Configs.EXPORT_MODEL_NAMES:
    output_dir = output_root + f"/{model_name}";

    print(f'Exporting {model_name} ============');
    print("Output Directory: ", output_dir);
    display_registered_model_uri(model_name);

    export_model(
        model_name = model_name, 
        output_dir = output_dir,
        stages = stages,
        versions = versions,
        export_latest_versions = export_latest_versions,
        export_version_model = export_version_model,
        export_permissions = export_permissions,
        notebook_formats = notebook_formats
    )
