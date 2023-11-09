# MLflow Export Import - Copy Tools

## Overview

* Copy MLflow objects to either the current or to another MLflow server (Databricks workspace).
* Currently only copy model version and copy run are supported.
* See also [Databricks notebooks](databricks_notebooks/copy).

Last updated: 2023-11-08.


## Copy Model Version

Oversion:
* Copies a model version and its run (deep copy).
* The new model version can be either in the same MLflow registry server  or in another.
* For Databricks, supports both standard Workspace (WS) and new Unity Catalog (UC) model registries.
* Databricks registry URIs should be [Databricks profiles](https://docs.databricks.com/en/dev-tools/cli/profiles.html).

In the two diagram below, the left _shallow copy_ is bad, while the right _deep copy_ is good.

### Unity Catalog Model Registry

<img src="diagrams/Copy_Model_Version_UC.png" height="440" />

### Workspace Model Registry

<img src="diagrams/Copy_Model_Version_NonUC.png" height="380" />

The option `--copy-lineage-tags` will copy metadata info from the source version and run to the 
new version and store it as tags starting with `mlflow_exim`.

#### Version and Run Lineage Tags

```
"mlflow_exim.src_version.name": "dev.models.sklearn_wine",
"mlflow_exim.src_version.version": "1",
"mlflow_exim.src_version.run_id": "c62ccf932e0649a2b9247cc76d89b637",
"mlflow_exim.src_client.tracking_uri": "databricks",
"mlflow_exim.mlflow_exim.dst_client.tracking_uri": "databricks",
"mlflow_exim.src_run.mlflow.databricks.workspaceURL": "huron.cloud.mycompany.com",
"mlflow_exim.src_run.mlflow.databricks.webappURL": "https://huron.mycompany.com",
"mlflow_exim.src_run.mlflow.databricks.workspaceID": "1812751281203379",
"mlflow_exim.src_run.mlflow.user": "first.last@mycompany.com"
```

### Copy WS model version to another workspace as a WS model version.
```
copy-model-version \
  --src-model dev.models.sklearn_wine \
  --src-version 1 \
  --dst-model prod.models.sklearn_wine \
  --dst-experiment-name  /Users/first.last@mycompany.com/experiments/My_Experiment \
  --src-registry-uri: databricks://e2_demo \
  --dst-registry-uri: databricks://e2_dogfood
```

### Copy UC model version to another workspace as a UC model version.
```
copy-model-version \
  --src-model dev.models.sklearn_wine \
  --src-version 1 \
  --dst-model prod.models.sklearn_wine \
  --dst-experiment-name  /Users/first.last@mycompany.com/experiments/My_Experiment \
  --src-registry-uri: databricks-uc://e2_demo \
  --dst-registry-uri: databricks-uc://e2_dogfood
```

### Copy WS model version to another workspace as a UC model version.
```
copy-model-version \
  --src-model Sklearn_Wine \
  --src-version 1 \
  --dst-model prod.models.sklearn_wine \
  --dst-experiment-name  /Users/first.last@mycompany.com/experiments/My_Experiment \
  --src-registry-uri: databricks://e2_demo \
  --dst-registry-uri: databricks-uc://e2_dogfood
```

### Copy local model version to Databricks workspace as UC model version
```
copy-model-version \
  --src-model Sklearn_Wine \
  --src-version 1 \
  --dst-model dev.models.sklearn_wine \
  --dst-experiment-name  /Users/first.last@mycompany.com/experiments/My_Experiment \
  --src-registry-uri: http://localhost:5020 \
  --dst-registry-uri: databricks-uc://e2_demo
```

### Usage
```
copy-model-version --help

Options:
  --src-model TEXT             Source registered model.  [required]
  --src-version TEXT           Source model version.  [required]
  --dst-model TEXT             Destination registered model.  [required]
  --src-registry-uri TEXT      Source MLflow registry URI.  [required]
  --dst-registry-uri TEXT      Destination MLflow registry URI.  [required]
  --dst-experiment-name TEXT   Destination experiment name. If specified, will
                               copy old version's run to a new run. Else, use
                               old version's run for new version.
  --copy-lineage-tags BOOLEAN  Add source lineage info to destination version
                               as tags starting with 'mlflow_exim'.  [default:
                               False]
  --verbose BOOLEAN            Verbose.  [default: False]
```
## Copy Run

### Examples

#### Open source MLflow
```
copy-run \
  --run-id c62ccf932e0649a2b9247cc76d89b637 \
  --experiment-name My_Experiment \
  --src-mlflow-uri http://localhost:5000 \
  --dst-mlflow-uri http://localhost:5001
```

#### Open source MLflow to Databricks MLflow

```
copy-run \
  --run-id c62ccf932e0649a2b9247cc76d89b637 \
  --experiment-name /Users/first.last@mycompany.com/experiments/My_Experiment \
  --src-mlflow-uri http://localhost:5000 \
  --dst-mlflow-uri databricks
```

#### Databricks to Databricks MLflow

```
copy-run \
  --run-id c62ccf932e0649a2b9247cc76d89b637 \
  --experiment-name /Users/first.last@mycompany.com/experiments/My_Experiment \
  --src-mlflow-uri databricks \
  --dst-mlflow-uri databricks://test-env
```

```
copy-run \
  --run-id c62ccf932e0649a2b9247cc76d89b637 \
  --experiment-name /Users/first.last@mycompany.com/experiments/My_Experiment \
  --src-mlflow-uri databricks://dev-env  \
  --dst-mlflow-uri databricks://test-env
```

### Usage
```
copy-run --help

Options:
  --run-id TEXT           Run ID.  [required]
  --experiment-name TEXT  Destination experiment name.  [required]
  --src-mlflow-uri TEXT   Source MLflow tracking server URI.  [required]
  --dst-mlflow-uri TEXT   Destination MLflow tracking server URI.  [required]
  --help                  Show this message and exit.
```
