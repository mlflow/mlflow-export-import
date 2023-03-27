# mlflow-export-import - Databricks Notebooks 


## Overview

* Set of Databricks notebooks to perform MLflow export and import operations.
* Use these notebooks when you want to copy MLflow objects from one Databricks workspace (tracking server) to another.
* In order to copy MLflow objects between workspaces, you will need to set up a shared cloud bucket mounted on each workspace's DBFS.
* The notebooks use [Git integration with Databricks Repos](https://docs.databricks.com/repos/index.html) though they can be run as a simple non-Repo workspace folder.
* See the [_README.py](_README.py) for more details.

## Databricks notebooks

There are two types of notebooks:
* Standard widget-based notebooks that call the MLflow Export Import API.
* Console script notebooks that use the shell to call the standard call Python scripts specified [here](https://github.com/mlflow/mlflow-export-import/blob/master/setup.py#L35).

### Standard widget-based notebooks

**Single Notebooks**

Copy one MLflow object and control its destination object name.

| Export | Import |
|----------|----------|
| [Export_Run](single/Export_Run.py) | [Import_Run](single/Import_Run.py) |
| [Export_Experiment](single/Export_Experiment.py) | [Import_Experiment.py](single/Import_Experiment.py) |
| [Export_Model](single/Export_Model.py) | [Import_Model.py](single/Import_Model.py) |


**Bulk notebooks**

Copy multiple MLflow objects. The target object name will be the same as the source object.

| Export | Import |
| ---- | ---- |
| [Export_Experiments](bulk/Export_Experiments.py) | [Import_Experiments](bulk/Import_Experiments.py) |
| [Export_Models](bulk/Export_Models.py) | [Import_Models](bulk/Import_Models.py) |
| [Export_All](bulk/Export_All.py) | Use [Import_Models](bulk/Import_Models.py) |

### Console script shell notebooks

Using Databricks `%sh` cell mode, you can execute MLflow Export Import scripts from the Linux shell.
See the [_README.py](scripts/_README.py) and and [Console_Scripts](scripts/Console_Scripts.py) notebook.

From a notebook you can then call a script such as:
```
export-model --help
```

## Import notebooks into Databricks workspace

You can load these notebooks into Databricks either as a workspace folder or a Git Repo.

### Load directory as Databricks workspace folder

See the [Workspace CLI](https://docs.databricks.com/dev-tools/cli/workspace-cli.html).
```
git clone https://github.com/mlflow/mlflow-export-import

databricks workspace import_dir \
  databricks_notebooks \
  /Users/me@mycompany.com/mlflow-export-import
```

### Clone directory as Databricks Git Repo

You can load a Git Repo either through the Databricks UI or via the command line.

#### 1. Load through Databricks UI

See [Clone a Git Repo & other common Git operations](https://docs.databricks.com/repos/git-operations-with-repos.html).

#### 2. Load from command line with curl

Note it's best to use the curl version since the CLI doesn't appear to support the sparse checkout option.

```
curl \
  https://my.company.com/api/2.0/repos \
  -H "Authorization: Bearer MY_TOKEN" \
  -X POST \
  -d ' {
    "url": "https://github.com/mlflow/mlflow-export-import",
    "provider": "gitHub",
    "path": "/Repos/me@my.company.com/mlflow-export-import",
    "sparse_checkout": {
      "patterns": [ "databricks_notebooks" ]
      }
    }'
```

