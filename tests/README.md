# mlflow-export-import - Tests

There are two types of tests:
* [Open source tests](open_source/README.md) - Launches a source and destination tracking server and runs tests to ensure that the exported MLflow object are correctly imported.
* [Databricks tests](databricks/README.md) - Launches Databricks jobs to ensure that [Databricks export-import notebooks](../databricks_notebooks/README.md) execute properly.
