# mlflow-export-import - OSS Tests

## Overview

There are two types of tests:
* OSS tests - Launch a source and destination tracking server and run tests to ensure that the exported MLflow object is correctly imported.
This page.
* [Databricks tests](databricks/README.md) - Tests that check if the Databricks export-import notebooks execute properly.
## Setup

Virtual environment
```
conda env create conda.yaml
conda activate mlflow-export-import-tests
```

## Test environment variables

|Name | Required | Description|
|-----|----------|---------|
| MLFLOW_TRACKING_URI_SRC | yes | URI of source tracking server |
| MLFLOW_TRACKING_URI_DST | yes | URI of destination tracking server |
| MLFLOW_EXPORT_IMPORT_OUTPUT_DIR | no | If set will use this as the export output directory instead of `tempfile.TemporaryDirectory()` |

## Run tests

Use the [run_tests.sh](run_tests.sh) script to run the tests and and specify the source and destination tracking server port number.
Output can be found in the `run_tests.log` file.

The script does the following:
* Launches a source MLflow tracking server and destination MLflow tracking server in the background.
* Runs tests against these servers with pytest.
* Kills the two MLflow tracking servers.

**Example**
```
run_tests.sh 5005 5006
```
```
======================== 43 passed in 295.36s (0:04:55) ========================
```
