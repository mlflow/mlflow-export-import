# Databricks Notebooks for MLflow Export and Import


## Overview

* Set of Databricks notebooks to perform MLflow export and import operations.
* Use these notebooks when you want to migrate MLflow objects from one Databricks workspace (tracking server) to another.
* The notebooks are generated with the Databricks [GitHub version control](https://docs.databricks.com/notebooks/github-version-control.html) feature.
* You will need to set up a shared cloud bucket mounted on DBFS in your source and destination workspaces.

## Import notebooks into Databricks workspace

To import the notebooks into your Databricks workspace you can either import an individual notebook or a directory of notebooks.

**Import a directory**

Use the [workspace import_dir](https://docs.databricks.com/dev-tools/cli/workspace-cli.html#import-a-directory-from-your-local-filesystem-into-a-workspace) Databricks CLI command.
```
databricks workspace import_dir individual/git /Users/me@mycompany.com/mlflow-export-import
```

**Import a notebook**

Use the [workspace import](https://docs.databricks.com/dev-tools/cli/workspace-cli.html#import-a-file-from-your-local-filesystem-into-a-workspace) Databricks CLI command.
```
databricks workspace import --language PYTHON individual/git/ImportRun.py  /Users/me@mycompany.com/mlflow-export-import/_README 
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
| Export_Run | [link](individual/git/Export_Run.py) | [link](individual/html/Export_Run.html) |
| Import_Run | [link](individual/git/Import_Run.py) | [link](individual/html/Import_Run.html) | 
| Export_Experiment | [link](individual/git/Export_Experiment.py) | [link](individual/html/Export_Experiment.html) 
| Import_Experiment | [link](individual/git/Import_Experiment.py) | [link](individual/html/Import_Experiment.html) |
| Export_Model | [link](individual/git/Export_Model.py) | [link](individual/html/Export_Model.html) | 
| Import_Model | [link](individual/git/Import_Model.py) | [link](individual/html/Import_Model.html) |
| Common | [link](individual/git/Common.py) | [link](html/Common.individual/html) | 
| _README | [link](individual/git/_README) | [link](individual/html/_README.html) |


## Collection Databricks notebooks

| Export | Import |
| ---- | ---- |
| [Export_Experiments](collection/Export_Experiments.py) | [Import_Experiments](collection/Import_Experiments.py) |
| Export Model | Import Model |
| Export All | Import All |
