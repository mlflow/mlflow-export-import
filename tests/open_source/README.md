# mlflow-export-import - Open Source Tests

## Overview

Open source MLflow Export Import tests use two MLflow tracking servers: 
  * Source tracking for exporting MLflow objects.
  * Destination tracking server for importing the exported MLflow objects.

## Setup

See the [common test setup](../README.md#Setup) section.

## Test Configuration

Test environment variables.

|Name | Required | Description|
|-----|----------|---------|
| MLFLOW_TRACKING_URI_SRC | yes | URI of source tracking server |
| MLFLOW_TRACKING_URI_DST | yes | URI of destination tracking server |
| MLFLOW_EXPORT_IMPORT_OUTPUT_DIR | no | If set, will use this as the export output directory instead of `tempfile.TemporaryDirectory()` |



## Run tests

Use the [run_tests.sh](run_tests.sh) script to run the tests and and specify the source and destination tracking server port number.
Output will be in the `run_tests.log` file.

The script does the following:
* Launches a source MLflow tracking server and destination MLflow tracking server in the background.
* Runs tests against these servers with pytest.
* Tears down the two MLflow tracking servers.

**Example**
```
run_tests.sh 5005 5006
```
```
======================== 43 passed in 295.36s (0:04:55) ========================
```
