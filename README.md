# MLflow Export Import

This package provides tools to export and import MLflow objects (runs, experiments or registered models) from one MLflow tracking server (Databricks workspace) to another.
See the [Databricks MLflow Object Relationships](https://github.com/mlflow/mlflow-resources/blob/master/slides/Databricks_MLflow_Object_Relationships.pdf) slide deck.

## Useful Links
  * [Point tools README](README_point.md)
    * `export_experiment` [API](mlflow_export_import/experiment/export_experiment.py#L25-L30)
    * `export_model` [API](mlflow_export_import/model/export_model.py#L31-L35)
    * `export_run` [API](mlflow_export_import/run/export_run.py#L47-L51)
    * `import_experiment` [API](mlflow_export_import/experiment/import_experiment.py#L31-L35)
    * `import_model` [API](mlflow_export_import/model/import_model.py#L83-L91)
    * `import_run` [API](mlflow_export_import/run/import_run.py#L48-L54)
  * [Bulk tools README](README_bulk.md)
  * [Databricks notebooks for object export/import](databricks_notebooks/README.md).

## Architecture

<img src="architecture.png" height="330" />

## Overview

### Why use MLflow Export Import?
  * Share and collaborate with other data scientists in the same or another tracking server.
    * For example, clone a favorite experiment from another user in your own workspace.
  * Migrate experiments to another tracking server.
    * For example, promote a registered model version (and its associated run) from the development to the production tracking server.
  * Backup your MLflow objects.
  * Disaster recovery.

### Migration modes

|Source tracking server | Destination tracking server | Note |
|-------|------------|---|
| Open source | Open source | common |
| Open source | Databricks | less common |
| Databricks | Databricks |common |
| Databricks | Open source | rare |

### Two migration tool contexts 

* Open source MLflow Python CLI scripts - this page.
* [Databricks notebooks](databricks_notebooks/README.md).


### Two sets of migration tools

* [Point tools](README_point.md). Low-level tools to copy individual MLflow objects and have fine-grained control over the target names.
For example, if you wish to clone an experiment in the same tracking server (workspace), use these tools.
* [Bulk tools](README_bulk.md). High-level tools to copy an entire tracking server or the web of MLflow objects (runs and experiments) associated with registered models. 
Full object referential integrity is maintained as well as the original MLflow object names.
  * For registered models it exports:
    * All the latest versions of a model.
    * The run associated with the version.
    * The experiment that the run belongs to.

### Other
* [Miscellanous tools](README_tools.md) 

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
* The Databricks API does not support:
  * Importing a notebook with its entire revision history.
  * Linking an imported run with a given notebook revision.
* When you import a run, the link to its source notebook revision ID will not exist and thus the UI will point to a dead link.
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
pip install git+https:///github.com/mlflow/mlflow-export-import/#egg=mlflow-export-import
```

#### 2. Install from github clone
```
git clone https://github.com/mlflow/mlflow-export-import
cd mlflow-export-import
pip install -e .
```

### Databricks setup

There are two different ways to install the package.

#### 1. Install package in notebook

[Install notebook-scoped libraries with %pip](https://docs.databricks.com/libraries/notebooks-python-libraries.html#install-notebook-scoped-libraries-with-pip).


```
pip install git+https:///github.com/mlflow/mlflow-export-import/#egg=mlflow-export-import
```

#### 2. Install package as a wheel on cluster

Build the wheel artifact, upload it to DBFS and then [install it on your cluster](https://docs.databricks.com/libraries/cluster-libraries.html).

```
python setup.py bdist_wheel
databricks fs cp dist/mlflow_export_import-1.0.0-py3-none-any.whl {MY_DBFS_PATH}
```

### Databricks MLflow usage

To run the tools externally (from your laptop) against a Databricks tracking server (workspace) set the following environment variables.
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
