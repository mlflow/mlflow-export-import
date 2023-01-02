
# Options

## Common options 

`notebook-formats` - If exporting a Databricks run, the run's notebook revision can be saved in the specified formats (comma-delimited argument). Each format is saved in the notebooks folder of the run's artifact root directory as `notebook.{format}`. Supported formats are  SOURCE, HTML, JUPYTER and DBC. See Databricks [Export Format](https://docs.databricks.com/dev-tools/api/latest/workspace.html#notebookexportformat) documentation.

`use-src-user-id` -  Set the destination user ID to the source user ID. Source user ID is ignored when importing into Databricks since the user is automatically picked up from your Databricks access token.

`export-source-tags` - Exports source information under the `mlflow_export_import` tag prefix. See section below for details.

## MLflow Export Import Source Tags 

For ML governance purposes, original source run information is saved under the `mlflow_export_import` tag prefix in the destination MLflow object.


For details see [README_source_tags](README_source_tags.md).
