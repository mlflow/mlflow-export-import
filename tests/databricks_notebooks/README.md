# Mlflow Export Import - Databricks Notebook Tests 

## Overview

* Databricks tests that ensure that [Databricks export-import notebooks](../../databricks_notebooks/README.md) execute properly.
* For each test launches a Databricks job that invokes a Databricks notebook.
  * For know only single notebooks are tested. Bulk notebooks tests are a TODO.
* Currently these tests are a subset of the fine-grained OSS tests. Their main purpose is to ensure that the notebooks run without errors.
* Unlike the OSS tests which use two source and destination tracking servers, the Databricks tests use one tracking server (workspace). 
Imported object have `_imported_` added to the end of their name. Using a source and destination workspaces is a WIP.

## Setup

See [Setup](../../README.md#Setup) section.

## Test Configuration

### Target workspace

The testing framework select the workspace from the MLFLOW_TRACKING_URI environment variable.
The simplest way to run against a Databricks MLflow tracking server is to set it to `databricks`.
The default profile from the ~/.databrickscfg file will be used.

In order to specify a non-default profile, MLFLOW_TRACKING_URI looks like `databricks://my-profile`.
You can easily run the tests by passing the profile as an argument to run_tests.sh.
```
run_test.sh my-profile
```

### config.yaml 

The tests use `config.yaml` for environment configuration.
Copy [config.yaml.template](config.yaml.template) to `config.yaml` and adjust the properties for your workspace.

**`config.yaml` properties**

|Name | Required | Description|
|-----|----------|---------|
| ws_base_dir | yes | Workspace directory for the test notebooks and experiments. |
| dbfs_base_export_dir | yes | DBFS base directory for exported MLflow objects. |
| model_name | yes | Name of test registered model. |
| use_source_tags | no | Whether to test using source tags or not. Default is False. |
| run_name_prefix | yes | Prefix of the job run name. |
| cluster | yes | Either an existing cluster ID or cluster spec for new cluster. See below. |


### Cluster

Since each test laynches a remote Databricks job, using a job cluster for each test would be very slow since you would
need to spin up a cluster for each test.
Therefore, the test session uses one cluster for the entire session. It can be a new cluster or an existing cluster - see below.

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
use_source_tags: False
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

LOG_FILE    : run_tests.log
JUNIT REPORT: run_tests_junit.xml
HTML REPORT : run_tests_report.html

```
