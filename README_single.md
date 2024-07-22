# MLflow Export Import - Single Object Tools

## Overview

The `Single` tools allow you to export and import single MLflow objects between tracking servers (Databricks workspaces).
These tools allow you to specify a different destination object name.

For example, if you want to clone the experiment `/Mary/Experiment/Iris` under a new name, you can specify the target experiment name as `/John/Experiment/Iris`.

See sample JSON export files [here](README_export_format.md#sample-export-json-files).

### Tools

| MLflow Object | Documentation | Code |
|-------|-------|---|
| Registered Model | [export-model](#export-registered-model) | [code](mlflow_export_import/model/export_model.py) |
|    | [import-model](#import-registered-model) | [code](mlflow_export_import/model/import_model.py) |
| Model Version | [export-model-version](#export-model-version) | [code](mlflow_export_import/model_version/export_model_version.py) |
|    | [import-model-version](#import-model-version) | [code](mlflow_export_import/model_version/import_model_version.py) |
|    | [copy-model-version](README_copy.md#copy-model-version) | [code](mlflow_export_import/copy/copy_model_version.py) |
| Experiment | [export-experiment](#export-experiment) | [code](mlflow_export_import/experiment/export_experiment.py) |
|    | [import-experiment](#import-experiment) | [code](mlflow_export_import/experiment/import_experiment.py) |
| Run | [export-run](#export-run) | [code](mlflow_export_import/run/export_run.py) |
|  | [import-run](#import-run) | [code](mlflow_export_import/run/import_run.py) |
|  | [copy-run](README_copy.md#copy-run) | [code](mlflow_export_import/copy/copy_run.py) |

## Experiment Tools

### Export Experiment

Export an experiment to a directory.
Accepts either an experiment ID or name.

#### Usage

```
export-experiment --help

Options:
  --experiment TEXT              Experiment name or ID.  [required]
  --output-dir TEXT              Output directory.  [required]
  --run-ids TEXT                 List of run IDs to export (comma seperated).
  --export-permissions BOOLEAN   Export Databricks permissions.  [default:
                                 False]
  --run-start-time TEXT          Only export runs started after this UTC time
                                 (inclusive). Format: YYYY-MM-DD.
  --export-deleted-runs BOOLEAN  Export deleted runs.  [default: False]
  --check-nested-runs BOOLEAN    Check if run in the 'run-ids' option is a
                                 parent of nested runs and export all the
                                 nested runs.  [default: False]
  --notebook-formats TEXT        Databricks notebook formats. Values are
                                 SOURCE, HTML, JUPYTER or DBC (comma
                                 separated).
```

#### Examples

##### Export experiment by experiment ID:
```
export-experiment \
  --experiment 2 \
  --output-dir out
```

##### Export experiment by experiment name:
```
export-experiment \
  --experiment sklearn-wine \
  --output-dir out
```

##### Export selected runs:
```
export-experiment \
  --experiment sklearn-wine \
  --output-dir out \
  --run-ids 1eea5a4f49184781947d6761b7207b25,1320b260e894469a9b60b415a25e4062
```

##### Export selected nested runs:
```
export-experiment \
  --experiment sklearn-wine \
  --output-dir out \
  --run-ids 1eea5a4f49184781947d6761b7207b25 \
  --check-nested-runs True 
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

The [export directory](samples/oss_mlflow/single/experiments/basic) contains a [JSON export file](samples/oss_mlflow/single/experiments/basic/experiment.json)
for the experiment and a subdirectory for each run.
The [run directory](samples/oss_mlflow/single/experiments/basic/eb66c160957d4a28b11d3f1b968df9cd) contains a [JSON export file](samples/oss_mlflow/single/experiments/basic/eb66c160957d4a28b11d3f1b968df9cd/run.json) containing run metadata and an artifact folder directory.

Sample export directory
```
+-experiment.json
+-eb66c160957d4a28b11d3f1b968df9cd/
| +-run.json
| +-artifacts/
|   +-plot.png
|   +-model/
|     +-requirements.txt
|     +-python_env.yaml
|     +-model.pkl
|     +-conda.yaml
|     +-MLmodel
```


### Import Experiment

Import an experiment from a directory. Reads the manifest file to import the expirement and its runs.

The experiment will be created if it does not exist in the destination tracking server.
If the destination experiment already exists, the source runs will be added to it.

#### Usage
```
import-experiment --help

Options:
  --experiment-name TEXT        Destination experiment name  [required]
  --input-dir TEXT              Input directory  [required]
  --import-permissions BOOLEAN  Import Databricks permissions.  [default:
                                False]
  --import-source-tags BOOLEAN  Import source information for registered model
                                and its versions ad tags in destination
                                object.  [default: False]
  --use-src-user-id BOOLEAN     Set the destination user field to the source
                                user field.  Only valid for open source
                                MLflow.  When importing into Databricks, the
                                source user field is ignored since it is
                                automatically picked up from your Databricks
                                access token.  There is no MLflow API endpoint
                                to explicity set the user_id for Run and
                                Registered Model.
  --dst-notebook-dir TEXT       Databricks destination workpsace base
                                directory for notebook. A run ID will be added
                                to contain the run's notebook.
  --help                        Show this message and exit.
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


## Run Tools

### Export run

Export run to directory.

**Usage**

```
export-run --help

Options:
  --run-id TEXT                   Run ID.  [required]
  --output-dir TEXT               Output directory.  [required]
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
+-run.json
+-artifacts/
| +-model/
|   +-requirements.txt
|   +-python_env.yaml
|   +-model.pkl
|   +-conda.yaml
|   +-MLmodel
```

Sample run.json files:
[OSS](samples/oss_mlflow/single/experiments/basic/eb66c160957d4a28b11d3f1b968df9cd/run.json)
\- [Databricks](samples/databricks/single/experiments/notebook_experiments/workspace_notebook/f7816bc76f254f22ab25549a7c2c9b06/run.json).


### Import run

Imports a run from a directory.

#### Usage

```
import-run --help

Options:
  --input-dir TEXT              Input directory.  [required]
  --experiment-name TEXT        Destination experiment name.  [required]
  --import-source-tags BOOLEAN  Import source information for registered model
                                and its versions ad tags in destination
                                object.  [default: False]
  --use-src-user-id BOOLEAN     Set the destination user field to the source
                                user field.  Only valid for open source
                                MLflow.  When importing into Databricks, the
                                source user field is ignored since it is
                                automatically picked up from your Databricks
                                access token.  There is no MLflow API endpoint
                                to explicity set the user_id for Run and
                                Registered Model.  [default: False]
  --dst-notebook-dir TEXT       Databricks destination workpsace base
                                directory for notebook. A run ID will be added
                                to contain the run's notebook.
  --mlmodel-fix BOOLEAN         Add correct run ID in destination MLmodel
                                artifact. Can be expensive for deeply nested
                                artifacts.  [default: True]
```

#### Import examples

##### Local import example
```
export MLFLOW_TRACKING_URI=databricks

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
  --experiment-name /Users/me@mycompany.com/imported/SklearnWine
```

## Registered Model Tools

### Export Registered Model

Export a registered model to a directory.
The default is to export all versions of a model including all `None` and `Archived` stages.
You can specify a list of stages to export.

Source: [export_model.py](mlflow_export_import/model/export_model.py).

#### Usage
```
export-model --help

Options:
  --model TEXT                    Registered model name.  [required]
  --output-dir TEXT               Output directory.  [required]
  --stages TEXT                   Stages to export (comma separated). Default
                                  is all stages and all versions. Stages are
                                  Production, Staging, Archived and None.
                                  Mututally exclusive with option --versions.
  --versions TEXT                 Export specified versions (comma separated).
                                  Mututally exclusive with option --stages.
  --export-latest-versions BOOLEAN
                                  Export latest registered model versions
                                  instead of all versions.  [default: False]
  --export-version-model BOOLEAN  Export registered model version's 'cached'
                                  MLflow model.  [default: False]
  --export-deleted-runs BOOLEAN   Export deleted runs.  [default: False]
  --export-permissions BOOLEAN    Export Databricks permissions.  [default:
                                  False]
  --notebook-formats TEXT         Databricks notebook formats. Values are
                                  SOURCE, HTML, JUPYTER or DBC (comma
                                  separated).
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
|   +-sklearn-model/
|   | +-model.pkl
|   | +-conda.yaml
|   | +-MLmodel
|   |
+-model.json
```

Sample model.json files:
[OSS](samples/oss_mlflow/single/models/basic/model.json)
\- [Databricks](samples/databricks/single/models/basic/model.json).
```
{
"mlflow": {
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
  --input-dir TEXT              Input directory  [required]
  --model TEXT                  Registered model name.  [required]
  --experiment-name TEXT        Destination experiment name  [required]
  --delete-model BOOLEAN        If the model exists, first delete the model
                                and all its versions.  [default: False]
  --import-permissions BOOLEAN  Import Databricks permissions using the HTTP
                                PATCH method.  [default: False]
  --import-source-tags BOOLEAN  Import source information for registered model
                                and its versions ad tags in destination
                                object.  [default: False]
  --await-creation-for INTEGER  Await creation for specified seconds.
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
  2 versions
Deleting 1 versions for model 'sklearn_wine_imported'
  version=2 status=READY stage=Production run-id=f93d5e4d182e4f0aba5493a0fa8d9eb6
Importing versions:
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

## Model Version Tools

### Export Model Version

Exports a registered model version and its run.
Also exports registered model and experiment metadata (description and tags).

Source: [export_model_version.py](mlflow_export_import/model_version/export_model_version.py).

#### Example
```
export-model-version \
  --model my_catalog.models.Sklearn_Wine \
  --version 1 \
  --output-dir dbfs:/mnt/mlflow-export-import/Sklearn_Wine
```

#### Usage
```
export-model-version --help

Options:
  --model TEXT                    Registered model name.  [required]
  --version TEXT                  Registered model version.  [required]
  --output-dir TEXT               Output directory.  [required]
  --export-version-model BOOLEAN  Export registered model version's 'cached'
                                  MLflow model.  [default: False]
  --export-permissions BOOLEAN    Export Databricks permissions.  [default:
                                  False]
  --notebook-formats TEXT         Databricks notebook formats. Values are
                                  SOURCE, HTML, JUPYTER or DBC (comma
                                  separated).
```

### Import Model Version

Imports a registered model version and its run. 

Optionally import the registered model and experiment metadata (description and tags) only if they are being created for the first time.
Will not modify metadata of an existing registered model and experiment.

Source: [import_model_version.py](mlflow_import_import/model_version/import_model_version.py).

#### Example
```
import-model-version \
  --input-dir dbfs:/mnt/mlflow-export-import/Sklearn_Wine \
  --model my_catalog.models.Sklearn_Wine \
  --create-model True \
  --experiment-name /Users/me@mycompany.com/SklearnWine
```

#### Usage
```
import-model-version --help

Usage: import-model-version
           [OPTIONS]

  Imports a registered model version and its run.

Options:
  --model TEXT                    Registered model name.  [required]
  --experiment-name TEXT          Destination experiment name for the
                                  version's run.  [required]
  --input-dir TEXT                Input directory.  [required]
  --create-model BOOLEAN          Create registered model before creating
                                  model version.  [default: False]
  --import-permissions BOOLEAN    Import Databricks permissions using the HTTP
                                  PATCH method.  [default: False]
  --import-source-tags BOOLEAN    Import source information for registered
                                  model and its versions and tags in
                                  destination object.  [default: False]
  --import-stages-and-aliases BOOLEAN
                                  Import stages and aliases.  [default: False]
  --import-metadata BOOLEAN       Import registered model and experiment
                                  metadata (description and tags).  [default:
                                  False]
```
