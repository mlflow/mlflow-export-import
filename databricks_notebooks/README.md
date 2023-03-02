# mlflow-export-import - Databricks Notebooks 


## Overview

* Set of Databricks notebooks to perform MLflow export and import operations.
* Use these notebooks when you want to copy MLflow objects from one Databricks workspace (tracking server) to another.
* In order to copy MLflow objects between workspaces, you will need to set up a shared cloud bucket mounted on each workspace's DBFS.
* The notebooks are generated with the Databricks [GitHub version control](https://docs.databricks.com/notebooks/github-version-control.html) feature.

## Import notebooks into Databricks workspace

Use the Databricks REST API command [databricks workspace import_dir](https://docs.databricks.com/dev-tools/cli/workspace-cli.html#import-a-directory-from-your-local-filesystem-into-a-workspace) to import the notebooks into a workspace.
```
git clone https://github.com/mlflow/mlflow-export-import
databricks workspace import_dir \
  databricks_notebooks \
  /Users/me@mycompany.com/tools
```

## Databricks notebooks

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
