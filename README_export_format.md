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

| Mode | OSS | Databricks |
|----|---|---|
| Individual | [Experiments](samples/oss_mlflow/single/experiments) | [Experiments](samples/databricks/single/experiments) |
| Individual | [Models](samples/oss_mlflow/single/models) | [Models](samples/databricks/single/models) |
| Collection | [Experiments](samples/oss_mlflow/bulk/experiments) | [Experiments](samples/databricks/bulk/experiments) |
| Collection | [Models](samples/oss_mlflow/bulk/models) | [Models](samples/databricks/bulk/models) |

