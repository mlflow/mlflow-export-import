# mlflow-export-import - Databricks Tests 

## Overview

* Databricks tests check that [Databricks export-import notebooks](../../databricks_notebooks/README.md) execute properly.
* Launches Databricks jobs that invoke a Databricks notebook.
* Currently these tests are a subset of the OSS tests. The main purpose is to ensure that the notebooks run correctly.
* Unlike the OSS tests which uses two source and destination tracking servers, the Databricks tests use one tracking cluster (workspace). Imported object have `_imported` added to the end of their name. Using a source and destination workspaces is a TODO.

## Setup

See [common test setup](../README.md#Setup) section.

## Test Configuration

The tests use `config.yaml` for environment configuration.
Copy [config.yaml.template](config.yaml.template) to `config.yaml` and adjust the properties for your workspace.

**`config.yaml` properties**

|Name | Required | Description|
|-----|----------|---------|
| ws_base_dir | yes | Workspace directory for the test notebooks and experiment. |
| dbfs_base_export_dir | yes | DBFS base directory for exported MLflow objects. |
| local_artifacts_compare_dir | no | Local scratch directory for comparing a source and destination run's downloaded artifacts. Defaults to a `/tmp` directory. For debugging, you can set to a fixed directory. |
| model_name | yes | Name of test registered model. |
| run_name_prefix | yes | Prefix of the job run name. |
| cluster | yes | Either an existing cluster ID or cluster spec for new cluster. See below. |
| profile | no | Databricks profile. If not set the DEFAULT profile from `~/.databrickscfg` will be used. |


### Cluster

Since each test invokes a remote Databricks job, using a job cluster for each test would be very slow since you would
need to spin up a cluster for each test.
Therefore, an interactive cluster is used for the test session. 

The `cluster` attribute is a polymorphic attribute that has two possible values:

* **New cluster**. Launch a new all-purpose (interactive) cluster at test startup time and reuse this cluster for all tests. 
At the end of the test suite, the cluster will be deleted.
In the `cluster` attribute specify a new cluster spec per the standard Databricks JSON format for [new_cluster](https://docs.databricks.com/dev-tools/api/latest/clusters.html#create) attribute.
* **Existing cluster**. Use an existing cluster. In the `cluster` attribute specify an existing cluster ID.

### Sample `config.yaml` files

**Use new cluster**

```
ws_base_dir: /Users/me.lastname@mycomany.com/tmp/test-mlflow-exim
dst_base_dir: dbfs:/tmp/me.lastname@mycomany.com/test-mlflow-exim
model_name: test-mlflow-exim
run_name_prefix: test-mlflow-exim
cluster: { 
  cluster_name: test-mlflow-exim,
  spark_version: 11.0.x-cpu-ml-scala2.12,
  node_type_id: i3.xlarge,
  num_workers: 1,
  autotermination_minutes: 20
}
```
**Use existing cluster**
```
ws_base_dir: /Users/me.lastname@mycomany.com/tmp/test-mlflow-exim
dst_base_dir: dbfs:/tmp/me.lastname@mycomany.com/test-mlflow-exim
model_name: test-mlflow-exim
run_name_prefix: test-mlflow-exim
cluster: 318-151752-abed99
```

## Run tests

Use the [run_tests.sh](run_tests.sh) script to run the tests. Output can be found in the `run_tests.log` file.

**Example**
```
run_tests.sh 
```
```
================== 7 passed, 6 warnings in 114.62s (0:01:54) ===================

```
