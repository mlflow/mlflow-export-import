# MLflow Export Import

The MLflow Export Import package provides tools to copy MLflow objects (runs, experiments or registered models) from one MLflow tracking server (Databricks workspace) to another.
Using the MLflow REST API, the tools export MLflow objects to an intermediate directory and then import them into the target tracking server.

For more details:
* [JSON export file format](README_export_format.md).
* [MLflow Object Relationships](https://github.com/amesar/mlflow-resources/blob/master/slides/Databricks_MLflow_Object_Relationships.pdf) slide deck.

## Architecture

<img src="architecture.png" height="330" />

## Overview

### Why use MLflow Export Import?
  * MLOps CI/CD. Migrate runs (or registered models) to another tracking server.
    * Promote a run from the development to the test tracking server.
    * After it passes tests, then promote it to the production tracking server.
  * Share and collaborate with other data scientists in the same or other tracking server (Databricks workspace).
    * For example, copy an experiment from one user to another.
  * Backup your MLflow objects to external storage so they can be restored if needed.
  * Disaster recovery. Save your MLflow objects to external storage so they can be replicated to another tracking server.

### MLflow Export Import scenarios

|Source tracking server | Destination tracking server | Note |
|-------|------------|---|
| Open source | Open source | common |
| Open source | Databricks | less common |
| Databricks | Databricks |common |
| Databricks | Open source | rare |

### MLflow Objects

These are the MLflow objects and their attributes that can be exported.

| Object | REST | Python | SQL |
|----|---|---|--|
| Run | [link]( https://mlflow.org/docs/latest/rest-api.html#run) | [link](https://mlflow.org/docs/latest/python_api/mlflow.entities.html#mlflow.entities.Run) | [link](https://github.com/amesar/mlflow-resources/blob/master/database_schemas/schema_mlflow_2.0.1.sql#L166) |
| Experiment | [link](https://mlflow.org/docs/latest/rest-api.html#mlflowexperiment) | [link](https://mlflow.org/docs/latest/python_api/mlflow.entities.html#mlflow.entities.Experiment) | [link](https://github.com/amesar/mlflow-resources/blob/master/database_schemas/schema_mlflow_2.0.1.sql#L37) |
| Registered Model | [link](https://mlflow.org/docs/latest/rest-api.html#registeredmodel) | [link](https://mlflow.org/docs/latest/python_api/mlflow.entities.html#mlflow.entities.model_registry.RegisteredModel) | [link](https://github.com/amesar/mlflow-resources/blob/master/database_schemas/schema_mlflow_2.0.1.sql#L152) |
| Registered Model Version | [link](https://mlflow.org/docs/latest/rest-api.html#modelversion) | [link](https://mlflow.org/docs/latest/python_api/mlflow.entities.html#mlflow.entities.model_registry.ModelVersion) | [link](https://github.com/amesar/mlflow-resources/blob/master/database_schemas/schema_mlflow_2.0.1.sql#L102) |

## Tools Overview

There are two dimensions to the MLflow Export Import tools:
* Export of MLflow objects in single or bulk mode.
* Regular Python scripts or Databricks notebooks.

**Single and Bulk Tools**

The two export modes are:

* [Single tools](README_single.md). Copy a single MLflow object between tracking servers. 
These tools allow you to specify a different destination object name.
For example, if you want to clone the experiment `/Mary/Experiments/Iris` under a new name, you can specify the target experiment name as `/John/Experiments/Iris`.

* [Bulk tools](README_bulk.md). High-level tools to copy an entire tracking server or a collection of MLflow objects.
There is no option to change destination object names.
Full object referential integrity is maintained (e.g. an imported registered model version will point to the imported run that it refers to.

[Databricks notebooks](databricks_notebooks/README.md)
simply invoke the corresponding Python classes.
Note that only `Single` notebooks are currently available as examples.



## Limitations

See [README_limitations.md](README_limitations.md).

## Quick Start

Setup
```
pip install mlflow-export-import
```

Export experiment
```
export MLFLOW_TRACKING_URI=http://localhost:5000

export-experiment \
  --experiment sklearn-wine \
  --output-dir /tmp/export
```

Import experiment
```
export MLFLOW_TRACKING_URI=http://localhost:5001

import-experiment \
  --experiment-name sklearn-wine \
  --input-dir /tmp/export
```

## Setup

Supports python 3.8.


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

### Databricks notebook setup

There are two different ways to install the package in a Databricks notebook.

#### 1. Install package in notebook

See documentation: [Install notebook-scoped libraries with %pip](https://docs.databricks.com/libraries/notebooks-python-libraries.html#install-notebook-scoped-libraries-with-pip).


```
%pip install mlflow-export-import
```

#### 2. Install package as a wheel on cluster

Build the wheel artifact, upload it to DBFS and then [install it on your cluster](https://docs.databricks.com/libraries/cluster-libraries.html).

```
git clone https://github.com/mlflow/mlflow-export-import
cd mlflow-export-import
python setup.py bdist_wheel
databricks fs cp dist/mlflow_export_import-1.0.0-py3-none-any.whl {MY_DBFS_PATH}
```

### Laptop to Databricks usage

To run the tools externally (from your laptop) against a Databricks tracking server (workspace) set the following environment variables:
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

## Other

* [README_options.md](README_options.md) advanced options.
* [Miscellanous tools](README_tools.md).

## Testing

There are two types of tests : open source and Databricks tests.
See [tests/README](tests/README.md) for details.

## README files

* [README.md](README.md)
* [README_single.md](README_single.md)
* [README_bulk.md](README_bulk.md)
* [README_tools.md](README_tools.md)
* [README_limitations.md](README_limitations.md)
* [README_options.md](README_options.md)
* [README_export_format.md](README_export_format.md)
* [tests/README.md](tests/README.md)
  * [tests/open_source/README.md](tests/open_source/README.md)
  * [tests/databricks/README.md](tests/databricks/README.md)
* [mlflow_export_import/workflow_api/README.md](mlflow_export_import/workflow_api/README.md)
* [databricks_notebooks/README.md](databricks_notebooks/README.md)
