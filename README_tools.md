# MLflow Export Import Tools

## Overview

Some useful miscellaneous tools.

Also see [experimental tools](mlflow_export_import/tools).

## Download notebook with revision

This tool downloads a notebook with a specific revision.

Note that the parameter `revision_timestamp` which represents the revision ID to the API endpoint `workspace/export` is not publicly documented.

**Usage**
```
download-notebook --help

Options:
  --output-dir TEXT        Output directory.  [required]
  --notebook TEXT          Notebook path.  [required]
  --revision TEXT          Notebook revision. If not specified will download
                           the latest revision.
  --notebook-formats TEXT  Databricks notebook formats. Values are SOURCE,
                           HTML, JUPYTER or DBC (comma seperated).  [default:
                           SOURCE]
```

**Example**
```
download-notebook \
  --output-dir out \
  --notebook /Users/andre@mycompany.com/mlflow/02a_Sklearn_Train_Predict \
  --revision 12345 \
  --notebook-formats SOURCE,DBC
```

```
ls -c1 out

02a_Sklearn_Train_Predict.dbc
02a_Sklearn_Train_Predict.source
```

## Call http_client - MLflow API or Databricks API

A convenience script to directly invoke either the MLflow API or Databricks API.

**Usage**
```
http-client --help

Options:
Options:
  --api TEXT          API: mlflow|databricks.
  --resource TEXT     API resource such as 'experiments/search'.  [required]
  --method TEXT       HTTP method: GET|POST|PUT|PATCH|DELETE.
  --params TEXT       HTTP GET query parameters as JSON.
  --data TEXT         HTTP request entity body as JSON (for POST, PUT and
                      PATCH).
  --output-file TEXT  Output file.
```

**HTTP GET example**
```
export MLFLOW_TRACKING_URI=http://localhost:5000

http-client \
  --resource experiments/list \
  --output-file experiments.json
```

**HTTP GET example - Databricks API**
```
http-client \
  --api databricks \
  --resource clusters/list \
  --output-file experiments.json
```

**HTTP POST example**
```
export MLFLOW_TRACKING_URI=http://localhost:5000

http-client \
  --resource experiments/create \
  --data '{"name": "my_experiment"}'
```

## List all registered models

Calls the `registered-models/list` MLflow API endpoint and creates the file `registered_models.json`.
```
list-models
```

```
{
  "registered_models": [
    {
      "name": "keras_mnist",
      "creation_timestamp": "1601399113433",
      "last_updated_timestamp": "1601399504920",
      "latest_versions": [
        {
          "name": "keras_mnist",
          "version": "1",
          "creation_timestamp": "1601399113486",
          "last_updated_timestamp": "1601399504920",
          "current_stage": "Archived",
          "description": "",
          "source": "file:///opt/mlflow/server/mlruns/1/9176458a78194d819e55247eee7531c3/artifacts/keras-model",
          "run_id": "9176458a78194d819e55247eee7531c3",
          "status": "READY",
          "run_link": ""
        },
```

## Workflow API

* [README.md](mlflow_export_import/workflow_api/README.md)
* The `WorkflowApiClient` is a Python wrapper around the Databricks REST API to execute job runs in a synchronous polling manner.
* Although a generic tool, in terms of mlflow-export-import, its main use is for testing Databricks notebook jobs.

