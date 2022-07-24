
use_src_user_id = "Set the destination user ID to the source user ID. Source user ID is ignored when importing into Databricks since setting it is not allowed."

export_source_tags = "Export source run metadata tags."

export_source_tags = "Export source run information (RunInfo, MLflow system tags starting with 'mlflow' and metadata) under the 'mlflow_export_import' tag prefix. See README_individual.md for more details."

notebook_formats = "Databricks notebook formats. Values are SOURCE, HTML, JUPYTER or DBC (comma seperated)."

model_stages = "Stages to export (comma seperated). Default is all stages. Values are Production, Staging, Archived and None."

delete_model = "If the model exists, first delete the model and all its versions."

use_threads = "Process export/import in parallel using threads."
