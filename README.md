# MLflow Export Import

Tools to export and import MLflow objects (runs, experiments or registered models) from one tracking server (Databricks workspace) to another.
For object relationips details see the [Databricks_MLflow_Object_Relationships](https://github.com/amesar/mlflow-resources/blob/master/slides/Databricks_MLflow_Object_Relationships.pdf) slide deck.

Some of the reasons to use MLflow Export Import
  * Share and collaborate with other data scientists in the same or another tracking server.
    * For example, you can a favorable experiment/run from another user to your own workspace.
  * Backup your experiments.
  * Migrate experiments to another tracking server.
  * Disaster recovery.

There are two modes to use MLflow Export Import
* Open source MLflow - As a normal Python package - this page.
* [Databricks notebooks](databricks_notebooks/README.md).
## Architecture

<img src="architecture.png" height="330" />

## Overview

There are two types of export-import tools:

* [Bulk tools](README_bulk.md) - high-level tools to copy an entire tracking server or the web of MLflow objects (runs and experiments) associated with registered models. 
A model's versions' runs and the runs' experiment are  transitively exported. 
Full object referential integrity is maintained as well as the original MLflow object names.
* [Point tools](README_point.md) - lower-level tools to copy individual MLflow objects and have fine-grained control over the target names.

## Limitations

### General Limitations

* Nested runs are only supported when you import an experiment. For a run, it is still a TODO.
* If the run linked to a registered model version does not exist (has been deleted) the version is not exported 
  since when importing [MLflowClient.create_model_version](https://mlflow.org/docs/latest/python_api/mlflow.tracking.html#mlflow.tracking.MlflowClient.create_model_version) requires a run ID.

### Databricks Limitations

#### Exporting Notebook Revisions
* The notebook revision associated with the run can be exported. It is stored as an artifact in the `notebooks` folder under the run's `artifacts` root.
*  You can save the notebook in the suppported SOURCE, HTML, JUPYTER and DBC formats. 

#### Importing Notebooks

* Partial functionality due to Databricks API limitations.
* The Databricks API does not support importing an entire notebook with all its revision history.
* The Databricks API does not support linking an imported run with a given notebook revision.
* When you import a run, the link to its source notebook revision ID will not exist and thus will not appear in the UI.
* As a convenience, the import tools allows you to import the exported notebook into Databricks. For more details, see:
  *  [README_point - Import run](README_point.md#Import-run)
  *  [README_point - Import experiment](README_point.md#Import-Experiment)
* The imported notebook cannot be attached to the run that created it.
* If you have several runs that point to different revisions of the same notebook, each imported run will be attached a different notebook.
* You must export a notebook in the SOURCE format for the notebook to be imported.


#### Used ID
* When importing a run or experiment, for open source MLflow you can specify the user owner. For Databricks import you cannot - the owner will be based on the personal access token (PAT) of the import user.

## Common options details 

`notebook-formats` - If exporting a Databricks run, the run's notebook revision can be saved in the specified formats (comma-delimited argument). Each format is saved in the notebooks folder of the run's artifact root directory as `notebook.{format}`. Supported formats are  SOURCE, HTML, JUPYTER and DBC. See Databricks [Export Format](https://docs.databricks.com/dev-tools/api/latest/workspace.html#notebookexportformat) documentation.

`use-src-user-id` -  Set the destination user ID to the source user ID. Source user ID is ignored when importing into Databricks since the user is automatically picked up from your Databricks access token.

`export-metadata-tags` - Creates metadata tags (starting with `mlflow_export_import.metadata`) that contain export information. These are the source `mlflow` tags in addition to other information. This is useful for provenance and auditing purposes in regulated industries.

```
Name                                          Value
mlflow_export_import.metadata.timestamp       1551037752
mlflow_export_import.metadata.timestamp_nice  2019-02-24 19:49:12
mlflow_export_import.metadata.experiment_id   2
mlflow_export_import.metadata.experiment-name sklearn_wine
mlflow_export_import.metadata.run-id          50fa90e751eb4b3f9ba9cef0efe8ea30
mlflow_export_import.metadata.tracking_uri    http://localhost:5000
```

## Setup

Supports python 3.7.6 or above.


### Local setup

First create a virtual environment.
```
python -m venv mlflow-export-import
source mlflow-export-import/bin/activate
```

There are two different ways to install the package.

#### 1. Install from github directly

```
pip install git+https:///github.com/amesar/mlflow-export-import/#egg=mlflow-export-import
```

#### 2. Install from github clone
```
git clone https://github.com/amesar/mlflow-export-import
cd mlflow-export-import
pip install -e .
```

### Databricks setup

There are two different ways to install the package.

#### 1. Install package in notebook

[Install notebook-scoped libraries with %pip](https://docs.databricks.com/libraries/notebooks-python-libraries.html#install-notebook-scoped-libraries-with-pip).


```
pip install git+https:///github.com/amesar/mlflow-export-import/#egg=mlflow-export-import
```

#### 2. Install package as a wheel on cluster

Build the wheel artifact, upload it to DBFS and then [install it on your cluster](https://docs.databricks.com/libraries/cluster-libraries.html).

```
python setup.py bdist_wheel
databricks fs cp dist/mlflow_export_import-1.0.0-py3-none-any.whl {MY_DBFS_PATH}
```

### Databricks MLflow usage

To run the tools against a Databricks tracking server (workspace) set the following environment variables.
```
export MLFLOW_TRACKING_URI=databricks
export DATABRICKS_HOST=https://mycompany.cloud.databricks.com
export DATABRICKS_TOKEN=MY_TOKEN
```
For full details see [Access the MLflow tracking server from outside Databricks](https://docs.databricks.com/applications/mlflow/access-hosted-tracking-server.html).


## Running tools

The main tool scripts can be executed either as a standard Python script or console script.

Python [console scripts](https://python-packaging.readthedocs.io/en/latest/command-line-scripts.html#the-console-scripts-entry-point)  (such as export-run, import-run, etc.) are provided as a convenience. For a list of scripts see [setup.py](setup.py).

This allows you to use:
```
export-experiment --help
```
instead of:
```
python -u -m mlflow_export_import.experiment.export_experiment --help
```
## Other tools

### Call http_client - MLflow API or Databricks API

A convenience script to directly invoke either the MLflow API or Databricks API.

**Usage**
```
http-client --help

Options:
  --api TEXT          API: mlflow|databricks.
  --resource TEXT     API resource such as 'experiments/list'.  [required]
  --method TEXT       HTTP method: GET|POST.
  --params TEXT       HTTP GET query parameters as JSON.
  --data TEXT         HTTP POST data as JSON.
  --output-file TEXT  Output file.
  --verbose BOOLEAN   Verbose.  [default: False]
```

**HTTP GET example**
```
export MLFLOW_TRACKING_URI=http://localhost:5000

http-client \
  --resource experiments/list\
  --output-file experiments.json
```

**HTTP POST example**
```
export MLFLOW_TRACKING_URI=http://localhost:5000

http-client \
  --resource experiments/create \
  --data '{"name": "my_experiment"}'
```
