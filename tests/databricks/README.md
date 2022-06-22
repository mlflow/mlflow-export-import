# mlflow-export-import - Databricks Tests 

## Overview

* Databricks tests check if the Databricks export-import notebooks execute properly.
* They launch a Databricks job that invokes a Databricks notebook.
* Currently these tests are minimal smoke tests that simply check to see if the notebooks can succesfully execute.
More complete test logic like the OSS tests will be added at a later date.

## Setup

See [parent tests README](../README.md#Setup)

## Test Configuration

The tests read in environment-specific properties from `config.yaml` file.

|Name | Required | Description|
|-----|----------|---------|
| ws_base_dir | yes | Workspace directory for the test notebooks and experiment |
| dst_base_dir | yes | DBFS path for exported MLflow objects |
| model_name | yes | Name of test registered model |
| run_name_prefix | yes | Prefix of the job run name |
| cluster_id | yes | Existing cluster ID |
| profile | no | Databricks profile. If not set the default DEFAULT from `~/.databrickscfg` will be used. |

Copy [config.yaml.template](config.yaml.template) to `config.yaml` and adjust the properties for your workspace.

Sample `config.yaml` file:

```
ws_base_dir: /Users/me.lastname@mycomany.com/tmp/test-mlflow-exim
dst_base_dir: dbfs:/tmp/me.lastname@mycomany.com/test-mlflow-exim
model_name: test-mlflow-exim
run_name_prefix: test-mlflow-exim
cluster_id: 0318-151752-abed99
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
