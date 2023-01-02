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
databricks workspace import_dir single/git /Users/me@mycompany.com/mlflow-export-import
```

**Import a notebook**

Use the [workspace import](https://docs.databricks.com/dev-tools/cli/workspace-cli.html#import-a-file-from-your-local-filesystem-into-a-workspace) Databricks CLI command.
```
databricks workspace import --language PYTHON single/git/ImportRun.py  /Users/me@mycompany.com/mlflow-export-import/_README 
```

**Note**

A separate _README import is needed since there is apparently a glitch in that when the _README file is checked into git, a `.py` extension is not added.


## Individual Databricks notebooks

**Columns**
* Notebook - name of notebook.
* git import - Databricks github sync format.
* HTML - Viewable convenience format. Note that the widgets are not displayed.

**Notebooks**

| Notebook | git code | HTML | 
|----------|----------|---------|
| Export_Run | [link](single/git/Export_Run.py) | [link](single/html/Export_Run.html) |
| Import_Run | [link](single/git/Import_Run.py) | [link](single/html/Import_Run.html) | 
| Export_Experiment | [link](single/git/Export_Experiment.py) | [link](single/html/Export_Experiment.html) 
| Import_Experiment | [link](single/git/Import_Experiment.py) | [link](single/html/Import_Experiment.html) |
| Export_Model | [link](single/git/Export_Model.py) | [link](single/html/Export_Model.html) | 
| Import_Model | [link](single/git/Import_Model.py) | [link](single/html/Import_Model.html) |
| Common | [link](single/git/Common.py) | [link](html/Common.single/html) | 
| _README | [link](single/git/_README) | [link](singlsingle/html/_README.html) |


## Bulk Databricks notebooks

| Export | Import |
| ---- | ---- |
| [Export_Experiments](bulk/Export_Experiments.py) | [Import_Experiments](bulk/Import_Experiments.py) |
| Export Model | Import Model |
| Export All | Import All |
