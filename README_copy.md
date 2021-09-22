# Copy MLflow Experiments, Runs or Models 

## Overview

* Directly copy an experiment or run from one tracking server to another.
* This functionality is less often used (and therefore tested) then export/import so your mileage may vary.

## Databricks Limitations

* Copy tools work only for open source MLflow.
* Copy tools do not work when both the source and destination trackings servers are Databricks MLflow.
* This is primarily because [MLflow client](https://github.com/mlflow/mlflow/blob/master/mlflow/tracking/client.py) constructor only accepts a tracking_uri. 
  * For open source MLflow this works fine and you can have the two clients (source and destination) in the same program with some workarounds.
  * For Databricks MLflow, the constructor is not used to initialize target servers. There is only one set environment variables (MLFLOW_TRACKING_URI, etc.) that is used to initialize the MLflowClient, so only one client instance can exist in a program.
* To copy experiments when a Databricks server is involved, use the the two-stage process of first exporting the experiment and then importing it.

## Experiments 

### Copy experiment from one tracking server to another

Copies an experiment from one MLflow tracking server to another.

Source: [copy_experiment.py](mlflow_export_import/experiment/copy_experiment.py).

In this example we use:
* Source tracking server runs on port 5000 
* Destination tracking server runs on 5001

**Usage**

```
python -m mlflow_export_import.experiment.copy_experiment --help

Options:
  --src-uri TEXT                  Source MLflow API URI.  [required]
  --dst-uri TEXT                  Destination MLflow API URI.  [required]
  --src-experiment TEXT           Source experiment ID or name.  [required]
  --dst-experiment-name TEXT      Destination experiment name.  [required]
  --use-src-user-id BOOLEAN       Set the destination user ID to the source
                                  user ID. Source user ID is ignored when
                                  importing into Databricks since setting it
                                  is not allowed.  [default: False]
  --export-metadata-tags BOOLEAN  Export source run metadata tags.  [default: False]
```

**Example**
```
python -u -m mlflow_export_import.experiment.copy_experiment \
  --src-experiment sklearn_wine \
  --dst-experiment-name sklearn_wine_imported \
  --src-uri http://localhost:5000 \
  --dst-uri http://localhost:5001
```

## Runs

### Copy run from one tracking server to another

Copies a run from one MLflow tracking server to another.

Source: [copy_run.py](mlflow_export_import/run/copy_run.py).

In this example we use
* Source tracking server runs on port 5000 
* Destination tracking server runs on 5001

**Usage**

```
python -m mlflow_export_import.run.copy_run --help

Options:
  --input TEXT                    Input path - directory or zip file.
                                  [required]

  --experiment-name TEXT          Destination experiment name.  [required]
  --use-src-user-id BOOLEAN       Set the destination user ID to the source
                                  user ID. Source user ID is ignored when
                                  importing into Databricks since setting it
                                  is not allowed.  [default: False]

  --import-mlflow-tags BOOLEAN    Import mlflow tags.  [default: True]
  --import-metadata-tags BOOLEAN  Import mlflow_tools tags.  [default: False]
```

**Example**
```
export MLFLOW_TRACKING_URI=http://localhost:5000

python -u -m mlflow_export_import.run.copy_run \
  --src-run-id 50fa90e751eb4b3f9ba9cef0efe8ea30 \
  --dst-experiment-name sklearn_wine \
  --src-uri http://localhost:5000 \
  --dst-uri http://localhost:5001
```


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
