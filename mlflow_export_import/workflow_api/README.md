# WorkflowApiClient

The WorkflowApiClient is a Python wrapper around the Databricks REST API to execute job runs in a synchronous polling manner.
Instead of each user stitching together different API calls to start a run and wait for it to finish, we bumdle this together as
a convenience tool.

## Overview

**General**

* Intended for Databricks job workflows.
* Supports [jobs/runs/submit](https://docs.databricks.com/api/latest/jobs.html#runs-submit).
* Launches a run and waits until it is finished (TERMINATED state) by 
  polling the [jobs/runs/get](https://docs.databricks.com/api/latest/jobs.html#runs-get) REST endpoint.
* [WorkflowApiClient](workflow_api_client.py) - main Python code.
* Although a generic tool, in terms of mlflow-export-import it used for testing Databricks notebook jobs.
* An improved version of the older [https://github.com/amesar/databricks-api-workflow](https://github.com/amesar/databricks-api-workflow).

**Details**
  * Launches a run based upon the standard Databricks JSON spec file.
  * Prints run ID.
  * Polls until cluster is created.
  * Prints cluster ID.
  * Polls until run is finished.
  * Print run result state and optionally the entire run JSON state.

## Limitations
* Supports the Jobs 2.0 API. Jobs 2.1 API support coming later.
* Support for [jobs/run-now](https://docs.databricks.com/api/latest/jobs.html#run-now) is coming later..
* Only supports notebook tasks. Other tasks coming later.

## Run Scripts

### run_submit

Code: [run_submit.py](run_submit.py).


**Options**
```
Options:
  --profile TEXT             Databricks profile
  --spec-file TEXT           JSON job specification file  [required]
  --sleep-seconds INTEGER    Sleep time for checking run status(seconds)
                             [default: 5]
  --timeout-seconds INTEGER  Timeout (seconds)  [default: 9223372036854775807]
  --verbose BOOLEAN          Verbose
```

**Run**

Note: run python with the `-u` option for unbuffered output so print statements are displayed in real-time.

```
python -u -m run_submit \
  --token MY_TOKEN \
  --spec-file job_spec.json \
  --sleep-seconds 3 \
  --timeout-seconds 300
```

```
Host: https://demo.cloud.databricks.com
2022-06-21 17:16:30 INFO New run_id: 5362830
2022-06-21 17:16:30 INFO Start waiting for 'cluster_is_created'.
2022-06-21 17:16:31 INFO Done waiting for 'cluster_is_created'. Cluster 0617-235336-61jzcmp1 has been created for run 5362830.
2022-06-21 17:16:31 INFO Processing time: 1.12 seconds
2022-06-21 17:16:31 INFO cluster_id: 0617-235336-61jzcmp1
2022-06-21 17:16:31 INFO Start waiting for 'run_is_done'. Run 5362830.
2022-06-21 17:16:32 INFO Waiting for 'run_is_done'. Run 5362830 is in RUNNING state.
. . .
2022-06-21 17:16:48 INFO Waiting for 'run_is_done'. Run 5362830 is in RUNNING state.
2022-06-21 17:16:49 INFO Waiting for 'run_is_done'. Run 5362830 is in TERMINATED state.
2022-06-21 17:16:49 INFO Processing time: 17.74 seconds
2022-06-21 17:16:49 WARNING No cluster log directory
2022-06-21 17:16:49 INFO Run result state: SUCCESS

```
