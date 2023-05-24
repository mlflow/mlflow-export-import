# Export file format

MLflow objects are exported in JSON format.

Each object export file is comprised of three JSON parts:
* system - internal export system information.
* info - custom object information.
* mlflow - MLflow object details from the MLflow REST API endpoint response.

**system**
```
"system": {
  "package_version": "1.1.2",
  "script": "export_experiment.py",
  "export_time": 1671248648,
  "_export_time": "2022-12-17 03:44:08",
  "mlflow_version": "2.0.1",
  "mlflow_tracking_uri": "http://localhost:5000",
  "user": "andre",
  "platform": {
    "python_version": "3.8.15",
    "system": "Darwin"
  }
},
```

**info**
```
"info": {
  "num_total_runs": 2,
  "num_ok_runs": 2,
  "num_failed_runs": 0,
  "failed_runs": []
},
```

**mlflow**
```
"mlflow": {
  "experiment": {
    "experiment_id": "1",
    "name": "sklearn_wine",
    "artifact_location": "/opt/mlflow/server/mlruns/1",
    "lifecycle_stage": "active",
    "tags": {
      "experiment_created": "2022-12-15 02:17:43",
      "version_mlflow": "2.0.1"
    },
    "creation_time": 1671248599410,
    "last_update_time": 1671248599410
  },
  "runs": [
    "4b0ce88fd34e45fc8ca08876127299ce",
    "4f2e3f75c845d4365addbc9c0262a58a5"
  ]
}
```


## Sample export JSON files 

### Open source and Databricks MLflow examples

Column legend:
* Basic - Basic default export.
* Src Tags - Import source tags into destination tracking server with `--import-source-tags`.

| Mode | Object | OSS    |          | Databricks |
|------|--------|--------|----------|------------|
|      |        | **Basic**  | **Src Tags** |     |
| Single | Experiment | [link](samples/oss_mlflow/single/experiments/basic) |[link](samples/oss_mlflow/single/experiments/src_tags) | [link](samples/databricks/single/experiments/basic) |
| Single | Model | [link](samples/oss_mlflow/single/models/basic/model.json) |[link](samples/oss_mlflow/single/models/src_tags/model.json) |  [link](samples/databricks/single/models) |
| Bulk | Experiment | [link](samples/oss_mlflow/bulk/experiments) | | [link](samples/databricks/bulk/experiments) | 
| Bulk | Model | [link](samples/oss_mlflow/bulk/experiments) || [link](samples/databricks/bulk/models) |


### Databricks MLflow experiment examples

There are two types of Databricks experiments: [workspace and notebook experiments](https://docs.databricks.com/mlflow/experiments.html#organize-training-runs-with-mlflow-experiments). When qualified by the two types of notebooks (workspace and repo notebook) this leads to 
the following four combinations:

* Workspace notebook with default notebook experiment.
* Workspace notebook with explictly set workspace experiment.
* Repo notebook with default notebook experiment.
* Repo notebook with explictly set workspace experiment.

Experiments can be generated from other sources besides the workspace UI.
Besides these four standard experiment types, there are also others:
* Automatically created experiments by AutoML.
* External Databricks jobs (can execute either a workspace or repo notebook)
* Externally running an [MLflow project against Databricks](https://docs.databricks.com/mlflow/projects.html).
* Externally calling the Databricks MLflow tracking API from your laptop.

Column legend:
* Mode - from where the experiment run is executed.
* Notebook - either a workspace or repo notebook or external.
For job 'github', the job task executes the notebook from github and not from the workspace.


| Mode | Notebook | Workspace experiment | Notebook experiment |
|-----|----|----|----|
| UI | Workspace | [link](samples/databricks/single/experiments/workspace_experiments/workspace_notebook) | [link](samples/databricks/single/experiments/notebook_experiments/workspace_notebook) |
| UI | Repo | [link](samples/databricks/single/experiments/workspace_experiments/repo_notebook) | [link](samples/databricks/single/experiments/notebook_experiments/repo_notebook) |
| UI AutoML | Workspace | [link](samples/databricks/single/experiments/workspace_experiments/automl_workspace_notebook) | |
| Job | Repo | [link](samples/databricks/single/experiments/workspace_experiments/job_repo_notebook) | |
| External MLflow project | github | | |
| External non-project | laptop | | |

For an example with "source tags", see [here](samples/databricks/single/experiments/workspace_experiments/workspace_notebook_src_tags).

