# mlflow-export-import - Databricks Notebooks 


## Overview

* Set of Databricks notebooks to perform MLflow export and import operations.
* Use these notebooks when you want to migrate MLflow objects from one Databricks workspace (tracking server) to another.
* The notebooks are generated with the Databricks [GitHub version control](https://docs.databricks.com/notebooks/github-version-control.html) feature.
* You will need to set up a shared cloud bucket mounted on DBFS in your source and destination workspaces.

## Import notebooks into Databricks workspace

To import the notebooks into your Databricks workspace you can either import an single notebook or a directory of notebooks.

**Import a directory**

Use the [workspace import_dir](https://docs.databricks.com/dev-tools/cli/workspace-cli.html#import-a-directory-from-your-local-filesystem-into-a-workspace) Databricks CLI command.
```
databricks workspace import_dir single /Users/me@mycompany.com/mlflow-export-import
```

**Import a notebook**

Use the [workspace import](https://docs.databricks.com/dev-tools/cli/workspace-cli.html#import-a-file-from-your-local-filesystem-into-a-workspace) Databricks CLI command.
```
databricks workspace import --language PYTHON single/ImportRun.py  /Users/me@mycompany.com/mlflow-export-import/_README 
```

**Note**

A separate _README import is needed since there is apparently a glitch in that when the _README file is checked into git, a `.py` extension is not added.


## Databricks notebooks

**Single Notebooks**

| Export | Import |
|----------|----------|
| [Export_Run](single/Export_Run.py) | [Import_Run](single/Import_Run.py) |
| [Export_Experiment](single/Export_Experiment.py) | [Import_Experiment.py](single/Import_Experiment.py) |
| [Export_Model](single/Export_Model.py) | [Import_Model.py](single/Import_Model.py) |


**Bulk notebooks**

| Export | Import |
| ---- | ---- |
| [Export_Experiments](bulk/Export_Experiments.py) | [Import_Experiments](bulk/Import_Experiments.py) |
| [Export_Models](bulk/Export_Models.py) | [Import_Models](bulk/Import_Models.py) |
| [Export_All](bulk/Export_All.py) | Use [Import_Models](bulk/Import_Models.py) |
