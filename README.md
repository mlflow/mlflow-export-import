# MLflow Export Import

This package provides tools to copy MLflow objects (runs, experiments or registered models) from one MLflow tracking server (Databricks workspace) to another.

For more details on MLflow objects (Databricks MLflow) see the [Databricks MLflow Object Relationships](https://github.com/amesar/mlflow-resources/blob/master/slides/Databricks_MLflow_Object_Relationships.pdf) slide deck.

## Architecture

<img src="architecture.png" height="330" />

## Overview

### Why use MLflow Export Import?
  * Share and collaborate with other data scientists in the same tracking server (Databricks workspace).
    * For example, clone an experiment from another user.
  * Share and collaborate with other data scientists in different tracking servers.
    * For example, clone an experiment from a different user in another tracking server.
  * MLOps CI/CD. Migrate runs (or registered models)  to another tracking server.
    * Promote a run from the development to the test tracking server.
    * After it passes tests, then promote it to the production tracking server.
  * Backup your MLflow objects to external storage so they can be restored if needed.
  * Disaster recovery. Save your MLflow objects to external storage so they can be replicated to another tracking server.

### MLflow Export Import scenarios

|Source tracking server | Destination tracking server | Note |
|-------|------------|---|
| Open source | Open source | common |
| Open source | Databricks | less common |
| Databricks | Databricks |common |
| Databricks | Open source | rare |

### Two sets of tools

* Open source MLflow Python scripts.
* [Databricks notebooks](databricks_notebooks/README.md) that invoke the Python scripts.

## Tools Overview

###  Python Scripts

There are two sets of Python scripts:

* [Individual tools](README_individual.md). Use these tools to copy individual MLflow objects between tracking servers. 
They allow you to specify a different destination object name.
For example, if you want to clone the experiment `/Mary/Experiments/Iris` under a new name, you can specify the target experiment name as `/John/Experiments/Iris`.

* [Collection tools](README_collection.md). High-level tools to copy an entire tracking server or a collection of MLflow objects.
Full object referential integrity is maintained as well as the original MLflow object names.

### Databricks notebooks

Databricks notebooks simply invoke their corresponding Python scripts.
Note that only `Individual` notebooks are currently available.

See [README](databricks_notebooks/individual/README.md).

### Other
* [Miscellanous tools](README_tools.md) 

## Limitations

### General Limitations

* Nested runs are only supported when you import an experiment. For a run, it is still a TODO.
* If the run linked to a registered model version does not exist (has been deleted) the version is not exported 
  since when importing [MLflowClient.create_model_version](https://mlflow.org/docs/latest/python_api/mlflow.client.html#mlflow.client.MlflowClient.create_model_version) requires a run ID.

### Databricks Limitations

#### Exporting Notebook Revisions
* The notebook revision associated with the run can be exported. It is stored as an an artifact in the run's `notebooks` artifact directory.
*  You can save the notebook in the suppported SOURCE, HTML, JUPYTER and DBC formats. 
*  Examples: `notebooks/notebook.dbc` or `notebooks/notebook.source`.

#### Importing Notebooks

* Partial functionality due to Databricks REST API limitations.
* The Databricks REST API does not support:
  * Importing a notebook with its revision history.
  * Linking an imported run with the imported notebook.
* When you import a run, the link to its source notebook revision ID will be a dead link and you cannot access the notebook from the MLflow UI.
* As a convenience, the import tools allows you to import the exported notebook into Databricks. For more details, see:
  *  [README_individual - Import run](README_individual.md#Import-run)
  *  [README_individual - Import experiment](README_individual.md#Import-experiment)
* You must export a notebook in the SOURCE format for the notebook to be imported.


#### Used ID
* When importing a run or experiment, for open source (OSS) MLflow you can specify a different user owner. 
* OSS MLflow - the destination run `mlflow.user` tag can be the same as the source `mlflow.user` tag since OSS MLflow allows you to set this tag.
* Databricks MLflow - you cannot set the `mlflow.user` tag.  The `mlflow.user` will be based upon the personal access token (PAT) of the importing user.

## Common options details 

`notebook-formats` - If exporting a Databricks run, the run's notebook revision can be saved in the specified formats (comma-delimited argument). Each format is saved in the notebooks folder of the run's artifact root directory as `notebook.{format}`. Supported formats are  SOURCE, HTML, JUPYTER and DBC. See Databricks [Export Format](https://docs.databricks.com/dev-tools/api/latest/workspace.html#notebookexportformat) documentation.

`use-src-user-id` -  Set the destination user ID to the source user ID. Source user ID is ignored when importing into Databricks since the user is automatically picked up from your Databricks access token.

`export-source-tags` - Exports source information under the `mlflow_export_import` tag prefix. See section below for details.

### MLflow Export Import Source Run Tags 

For ML governance purposes, original source run information is saved under the `mlflow_export_import` tag prefix. 


For details see [README_source_tags](README_source_tags.md).

## Setup

Supports python 3.7 or above.


### Local setup

First create a virtual environment.
```
python -m venv mlflow-export-import
source mlflow-export-import/bin/activate
```

There are several different ways to install the package.

#### 1. Install from PyPI - recommended

```
pip install mlflow-export-import
```

#### 2. Install from github directly

```
pip install git+https:///github.com/mlflow/mlflow-export-import/#egg=mlflow-export-import
```

#### 3. Install from github clone
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
pip install mlflow-export-import
```

#### 2. Install package as a wheel on cluster

Build the wheel artifact, upload it to DBFS and then [install it on your cluster](https://docs.databricks.com/libraries/cluster-libraries.html).

```
git clone https://github.com/mlflow/mlflow-export-import
cd mlflow-export-import
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

The main tool scripts can be executed either as a standard Python script or Command Line Utility.

To see the various subcommands and their documentation, try the following command:

```
mlflow-export-import --help
```

```console
❯ mlflow-export-import --help
Usage: mlflow-export-import [OPTIONS] COMMAND [ARGS]...

  MLflow Export / Import CLI: Command Line Interface

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  export-all          Export the entire tracking server.
  export-experiment   Exports an experiment to a directory.
  export-experiments  Exports experiments to a directory.
  export-model        Export a registered model.
  export-models       Exports models and their versions' backing.
  export-run          Exports a run to a directory.
  find-artifacts      Find artifacts that match a filename.
  http-client         Interact with the MLflow / Databricks HTTP Client.
  import-all          Imports models and their experiments and runs.
  import-experiment   Imports an experiment from a directory.
  import-experiments  Import a list of experiments from a directory.
  import-model        Import a registered model.
  import-run          Imports a run from a directory.
  list-models         Lists all registered models.
```

## Testing

Two types of tests exist: open source and Databricks tests.
See [tests/README](tests/README.md).

### Workflow API

* [README.md](mlflow_export_import/workflow_api/README.md)
* The `WorkflowApiClient` is a Python wrapper around the Databricks REST API to execute job runs in a synchronous polling manner.
* Although a generic tool, in terms of mlflow-export-import, its main use is for testing Databricks notebook jobs.

