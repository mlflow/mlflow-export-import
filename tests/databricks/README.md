# mlflow-export-import - Databricks Tests 

## Overview

* Databricks tests check if the Databricks export-import notebooks execute properly.
* They launch a Databricks job that invokes a Databricks notebook.
* Currently these tests are minimal smoke tests that simply check to see if the notebooks can succesfully execute.
More complete test logic like the OSS tests will be added at a later date.

## Setup

See [parent tests README](../README.md#Setup)

## Test Configuration

The tests use `config.yaml` for environment configuration.
Copy [config.yaml.template](config.yaml.template) to `config.yaml` and adjust the properties for your workspace.

The tests read in environment-specific properties from `config.yaml` file.

|Name | Required | Description|
|-----|----------|---------|
| ws_base_dir | yes | Workspace directory for the test notebooks and experiment |
| dbfs_base_export_dir | yes | DBFS base directory for exported MLflow objects |
| local_artifacts_compare_dir | no | Local scratch directory for comparing two run's downloaded artifacts. Defaults to a tmp directory. Set it for debugging. |
| model_name | yes | Name of test registered model |
| run_name_prefix | yes | Prefix of the job run name |
| cluster | yes | Either an existing cluster ID or cluster spec for new cluster. See below. |
| profile | no | Databricks profile. If not set the default DEFAULT from `~/.databrickscfg` will be used. |


### Cluster

Since each test invokes a remote Databricks job, using a job cluster for each test would be very slow since you would
need to spin up a cluster for each test.
Therefore an interactive cluster is used for the test session. 

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
================== 2 passed, 6 warnings in 114.62s (0:01:54) ===================

```
