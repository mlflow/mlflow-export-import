# mlflow-export-import - Tests

## Overview

There are two sets of tests:
* [Open source MLlflow tests](open_source/README.md). Substantial tests. Launches a source and destination tracking server and runs tests to ensure that the exported MLflow objects (runs, experiments and registered models) are correctly imported.
* [Databricks MLflow notebook tests](databricks/README.md). Smoke tests for Databricks notebooks. Launches Databricks jobs to ensure that [Databricks export-import notebooks](../databricks_notebooks/README.md) execute properly.

## Setup

Create a virtual environment with dependencies.
```
conda env create conda.yaml
conda activate mlflow-export-import-tests
```
