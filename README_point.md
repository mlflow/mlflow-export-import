# MLflow Export Import - Point tools

## Overview

"Point" tools export and individual MLflow object. 
They allow for more fine-grained low-level control such as object names.

### Experiments
  * Export experiment to a directory.
  * Import experiment from a directory.

### Runs
  * Export run to  a directory.
  * Import run from a directory.

### Registered Models
  * Export registered model to a directory.
  * Import registered model from a directory.
  * List all registered models.

## Experiments 

### Export Experiment

Export an experiment to a directory.
Accepts either an experiment ID or name.

#### Usage

```
export-experiment --help

Options:
  --experiment TEXT               Experiment name or ID.  [required]
  --output-dir TEXT               Output directory.  [required]
  --export-metadata-tags BOOLEAN  Export source run metadata tags.  [default: False]
  --notebook-formats TEXT         Notebook formats. Values are SOURCE, HTML,
                                  JUPYTER or DBC (comma seperated).  [default: ]
```

#### Examples

Export experiment by experiment ID.
```
export-experiment \
  --experiment 2 \
  --output-dir out
```

Export experiment by experiment name.
```
export-experiment \
  --experiment sklearn-wine \
  --output-dir out
```

#### Databricks export examples

See [Access the MLflow tracking server from outside Databricks](https://docs.databricks.com/applications/mlflow/access-hosted-tracking-server.html).
```
export MLFLOW_TRACKING_URI=databricks
export DATABRICKS_HOST=https://mycompany.cloud.databricks.com
export DATABRICKS_TOKEN=MY_TOKEN

export-experiment \
  --experiment /Users/me@mycompany.com/SklearnWine \
  --output-dir out \
  --notebook-formats DBC,SOURCE 
```

#### Export directory structure

The output directory contains a manifest file and a subdirectory for each run (by run ID).
The run directory contains a run.json
([OSS](samples/oss_mlflow/experiments/1/6ccadf17812d43929b093d75cca1c33f/run.json),
[Databricks](samples/databricks/experiments/sklearn_wine/16c36560c57a43fdb46e98f88a8d8819/run.json)),
file containing run metadata and an artifact hierarchy.

```
+-manifest.json
+-441985c7a04b4736921daad29fd4589d/
| +-artifacts/
|   +-plot.png
|   +-sklearn-model/
|     +-model.pkl
|     +-conda.yaml
|     +-MLmodel
```


### Import Experiment

Import an experiment from a directory. Reads the manifest file to import the expirement and their runs.

The experiment will be created if it does not exist in the destination tracking server. 
If the experiment already exists, the source runs will be added to it.

#### Usage
```
import-experiment --help \

Options:
  --input-dir TEXT                Input path - directory  [required]
  --experiment-name TEXT          Destination experiment name  [required]
  --just-peek BOOLEAN             Just display experiment metadata - do not import
  --use-src-user-id BOOLEAN       Set the destination user ID to the source
                                  user ID. Source user ID is ignored when
                                  importing into Databricks since setting it
                                  is not allowed.
  --dst-notebook-dir TEXT         Databricks destination workpsace base
                                  directory for notebook. A run ID will be
                                  added to contain the run's notebook.
```

#### Import examples

```
import-experiment \
  --experiment-name imported_sklearn \
  --input-dir out
```

#### Databricks import examples

```
export MLFLOW_TRACKING_URI=databricks
import-experiment \
  --experiment-name /Users/me@mycompany.com/imported/SklearnWine \
  --input-dir exported_experiments/3532228 \
```


## Runs

### Export run

Export run to directory.

**Usage**

```
export-run --help

Options:
  --run-id TEXT                   Run ID.  [required]
  --output-dir TEXT               Output directory.  [required]
  --export-metadata-tags BOOLEAN  Export source run metadata tags.  [default: False] 
  --notebook-formats TEXT         Notebook formats. Values are SOURCE, HTML,
                                  JUPYTER or DBC (comma seperated).  [default: ]
```


**Run examples**
```
export-run \
  --run-id 50fa90e751eb4b3f9ba9cef0efe8ea30 \
  --output-dir out
```

Produces a directory with the following structure:
```
run.json
artifacts
  plot.png
  sklearn-model
    MLmodel
    conda.yaml
    model.pkl
```
Sample run.json:
[OSS](samples/oss_mlflow/experiments/sklearn_wine/1/6ccadf17812d43929b093d75cca1c33f/run.json)
 \- [Databricks](samples/databricks/experiments/sklearn_wine/16c36560c57a43fdb46e98f88a8d8819/run.json).
```
{   
  "info": {
    "run-id": "50fa90e751eb4b3f9ba9cef0efe8ea30",
    "experiment_id": "2",
    ...
  },
  "params": {
    "max_depth": "16",
    "max_leaf_nodes": "32"
  },
  "metrics": {
    "rmse": [
      {
        "value": 0.7367947360663162,
        "timestamp": 1647391746393,
        "step": 0
      }
    ],
   "r2": [
      {
        "value": 0.28100217442439346,
        "timestamp": 1647391746422,
        "step": 0
      }
    ]
  },
  "tags": {
    "mlflow.source.git.commit": "a42b9682074f4f07f1cb2cf26afedee96f357f83",
    "mlflow.runName": "demo.sh",
    "run_origin": "demo.sh",
    "mlflow.source.type": "LOCAL",
    "mlflow_export_import.metadata.tracking_uri": "http://localhost:5000",
    "mlflow_export_import.metadata.timestamp": 1563572639,
    "mlflow_export_import.metadata.timestamp_nice": "2019-07-19 21:43:59",
    "mlflow_export_import.metadata.run-id": "130bca8d75e54febb2bfa46875a03d59",
    "mlflow_export_import.metadata.experiment_id": "2",
    "mlflow_export_import.metadata.experiment-name": "sklearn_wine"
  }
}
```

### Import run

Imports a run from a directory.

#### Usage

```
import-run --help

Options:
  --input-dir TEXT                Source input directory that contains the
                                  exported run.  [required]

  --experiment-name TEXT          Destination experiment name.  [required]
  --mlmodel-fix BOOLEAN           Add correct run ID in destination MLmodel
                                  artifact. Can be expensive for deeply nested
                                  artifacts.  [default: True]

  --use-src-user-id BOOLEAN       Set the destination user ID to the source
                                  user ID. Source user ID is ignored when
                                  importing into Databricks since setting it
                                  is not allowed.  [default: False]

  --dst-notebook-dir TEXT         Databricks destination workpsace directory
                                  for notebook import.
  --dst-notebook-dir-add-run-id TEXT
                                  Add the run ID to the destination notebook
                                  directory.
```

#### Import examples

Directory `out` is where you exported your run.

##### Local import example
```
import-run \
  --run-id 50fa90e751eb4b3f9ba9cef0efe8ea30 \
  --input out \
  --experiment-name sklearn_wine_imported
```

##### Databricks import example

```
export MLFLOW_TRACKING_URI=databricks
run.import-run \
  --run-id 50fa90e751eb4b3f9ba9cef0efe8ea30 \
  --input out \
  --experiment-name /Users/me@mycompany.com/imported/SklearnWine \
```

## Registered Models

### Export Registered Model

Export a registered model to a directory.
The default is to export all versions of a model including all None and Archived stages.
You can specify a list of stages to export.

Source: [export_model.py](mlflow_export_import/model/export_model.py).

#### Usage
```
export-model --help

Options:
  --model TEXT       Registered model name.  [required]
  --output-dir TEXT  Output directory.  [required]
  --export-metadata-tags BOOLEAN  Export source run metadata tags.  [default:
  --notebook-formats TEXT         Notebook formats. Values are SOURCE, HTML,
                                  JUPYTER or DBC (comma seperated).  [default: ]
                                  True]
  --stages TEXT                   Stages to export (comma seperated). Default
                                  is all stages. Values are Production,
                                  Staging, Archived and None
```

#### Example
```
export-model \
  --model sklearn_wine \
  --output-dir out \
  --stages Production,Staging
```
```
Found 6 versions
Exporting version 3 stage 'Production' with run_id 24aa9cce1388474e9f26d17100724cdd to out/24aa9cce1388474e9f26d17100724cdd
Exporting version 5 stage 'Staging' with run_id 8efd80f59b7946119d8f1838515eea25 to out/8efd80f59b7946119d8f1838515eea25
```

### Output

Output export directory example.

```
+-749930c36dee49b8aeb45ee9cdfe1abb/
| +-artifacts/
|   +-plot.png
|   +-sklearn-model/
|   | +-model.pkl
|   | +-conda.yaml
|   | +-MLmodel
|   |  
+-model.json
```

Sample model.json:
[OSS](samples/oss_mlflow/models/model.json)
\- [Databricks](samples/databricks/models/model.json).
```
{
  "registered_model": {
    "name": "sklearn_wine",
    "creation_timestamp": "1587517284168",
    "last_updated_timestamp": "1587572072601",
    "description": "hi my desc",
    "latest_versions": [
      {
        "name": "sklearn_wine",
        "version": "1",
        "creation_timestamp": "1587517284216",
. . .
```


### Import registered model

Import a registered model from a directory.

Source: [import_model.py](mlflow_export_import/model/import_model.py).

#### Usage

```
import-model --help

Options:
  --input-dir TEXT              Input directory produced by export_model.py.
                                [required]

  --model TEXT                  New registered model name.  [required]
  --experiment-name TEXT        Destination experiment name  - will be created
                                if it does not exist.  [required]
  --delete-model BOOLEAN        First delete the model if it exists and all
                                its versions.  [default: False]
  --await-creation-for INTEGER  Await creation for specified seconds.
  --verbose BOOLEAN             Verbose.  [default: False]
  --help                        Show this message and exit.
```


#### Example

```
import-model \
  --model sklearn_wine \
  --experiment-name sklearn_wine_imported \
  --input-dir out  \
  --delete-model True
```

```
Model to import:
  Name: sklearn_wine
  Description: my model
  2 latest versions
Deleting 1 versions for model 'sklearn_wine_imported'
  version=2 status=READY stage=Production run-id=f93d5e4d182e4f0aba5493a0fa8d9eb6
Importing latest versions:
  Version 1:
    current_stage: None:
    Run to import:
      run-id: 749930c36dee49b8aeb45ee9cdfe1abb
      artifact_uri: file:///opt/mlflow/server/mlruns/1/749930c36dee49b8aeb45ee9cdfe1abb/artifacts
      source:       file:///opt/mlflow/server/mlruns/1/749930c36dee49b8aeb45ee9cdfe1abb/artifacts/sklearn-model
      model_path: sklearn-model
      run-id: 749930c36dee49b8aeb45ee9cdfe1abb
    Importing run into experiment 'scratch' from 'out/749930c36dee49b8aeb45ee9cdfe1abb'
    Imported run:
      run-id: 03d0cfae60774ec99f949c42e1575532
      artifact_uri: file:///opt/mlflow/server/mlruns/13/03d0cfae60774ec99f949c42e1575532/artifacts
      source:       file:///opt/mlflow/server/mlruns/13/03d0cfae60774ec99f949c42e1575532/artifacts/sklearn-model
Version: id=1 status=READY state=None
Waited 0.01 seconds
```

### List all registered models

Calls the `registered-models/list` API endpoint and creates the file `registered_models.json`.
```
list-models
```

cat registered_models.json
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
