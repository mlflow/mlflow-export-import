# MLflow Export Import Source Tags

<h2>
<font color="red">
Deprecated - Update WIP
</font>
</h2>

## Overview

`export-source-tags` - Exports source information under the `mlflow_export_import` tag prefix. See section below for details.

## MLflow Export Import Source Run Tags

For governance purposes, original source run information is saved under the `mlflow_export_import` tag prefix. 
When you import a run, the values of `RunInfo` are auto-generated for you as well as some other tags. 

This is useful for model governance, provenance and auditing purposes for regulated industries such as finance and HLS (health care and life science).

If the `export-source-tags` option is set on an export tool, three sets of source run tags will be saved under the `mlflow_export_import` prefix.

* **MLflow system tags.** Prefix: `mlflow_export_import.mlflow`. Saves all source MLflow system tags starting with `mlflow.` 
  * For example, the source tag `mlflow.source.type` is saved as the destination tag `mlflow_export_import.mlflow.source.type`.

* **RunInfo field tags.** Prefix: `mlflow_export_import.run_info`. Saves all source [RunInfo](https://mlflow.org/docs/latest/python_api/mlflow.entities.html#mlflow.entities.RunInfo) fields.
  * For example `RunInfo.run_id` is stored as `mlflow_export_import.run_info.run_id`.
  * Note that since MLflow tag values must be a string, non-string `RunInfo` fields (int) are cast to a string such as `start_time`.

* **Metadata tags.** Prefix: `mlflow_export_import.metadata`.  Tags indicating source export metadata information 
  * Example: `mlflow_export_import.metadata.tracking_uri`.

## Open Source Mlflow Export Import Tags

See [sample run tags](samples/oss_mlflow/individual/experiments/sklearn_wine/eb66c160957d4a28b11d3f1b968df9cd/run.json).

#### MLflow system tags

|Tag | Value |
|----|-------|
| mlflow_export_import.mlflow.log-model.history | [{\run_id\: \f2e3f75c845d4365addbc9c0262a58a5\ | \artifact_path\: \model\, \utc_time_created\: \2022-06-12 03:34:39.289551\, \flavors\: {\python_function\: {\model_path\: \model.pkl\, \loader_module\: \mlflow.sklearn\, \python_version\: \3.7.6\, \env\: \conda.yaml\}, \sklearn\: {\pickled_model\: \model.pkl\, \sklearn_version\: \1.0.2\, \serialization_format\: \cloudpickle\, \code\: null}}, \model_uuid\: \38c43fc59c734b0a80704ac3214ea2c3\, \mlflow_version\: \1.26.1\}, {\run_id\: \f2e3f75c845d4365addbc9c0262a58a5\, \artifact_path\: \onnx-model\, \utc_time_created\: \2022-06-12 03:34:42.110784\, \flavors\: {\python_function\: {\loader_module\: \mlflow.onnx\, \python_version\: \3.7.6\, \data\: \model.onnx\, \env\: \conda.yaml\}, \onnx\: {\onnx_version\: \1.10.2\, \data\: \model.onnx\, \providers\: [\CUDAExecutionProvider\, \CPUExecutionProvider\], \code\: null}}, \model_uuid\: \ddf79625e4d241b7813e601f31b1222f\, \mlflow_version\: \1.26.1\}],
| mlflow_export_import.mlflow.runName | train.sh |
| mlflow_export_import.mlflow.source.git.commit | 67fb8f823ec794902cdbb67be653a6155a0b5172 |
| mlflow_export_import.mlflow.source.name | /Users/andre/git/mlflow-examples/python/sklearn/wine_quality/train.py |
| mlflow_export_import.mlflow.source.type | LOCAL |
| mlflow_export_import.mlflow.user | andre |

#### MLflow RunInfo tags

|Tag | Value |
|----|-------|
| mlflow_export_import.run_info.artifact_uri | /opt/mlflow/server/mlruns/2/f2e3f75c845d4365addbc9c0262a58a5/artifacts |
| mlflow_export_import.run_info.end_time | 1655004883611 |
| mlflow_export_import.run_info.experiment_id | 2 |
| mlflow_export_import.run_info.lifecycle_stage | active |
| mlflow_export_import.run_info.run_id | f2e3f75c845d4365addbc9c0262a58a5 |
| mlflow_export_import.run_info.start_time | 1655004878844 |
| mlflow_export_import.run_info.status | FINISHED |
| mlflow_export_import.run_info.user_id | andre |

#### Metadata tags

|Tag | Value | Description |
|----|-------|-------------|
| mlflow_export_import.metadata.mlflow_version | 1.26.1 | MLflow version |
| mlflow_export_import.metadata.tracking_uri | http://127.0.0.1:5020 | Source tracking server URI |
| mlflow_export_import.metadata.experiment_name | sklearn_wine | Name of experiment |
| mlflow_export_import.metadata.timestamp | 1655007510 | Time when run was exported |
| mlflow_export_import.metadata.timestamp_nice | 2022-06-12 04:18:30 | ibid |

## Databricks MLflow source tags

See [sample run tags](samples/databricks/individual/experiments/sklearn_wine/f2e3f75c845d4365addbc9c0262a58a5/run.json).

#### MLflow system tags 

|Tag | Value | 
|----|-------|
| mlflow_export_import.mlflow.databricks.cluster.id         | 0318-151752-abed99                                                                                             |
| mlflow_export_import.mlflow.databricks.cluster.info       | {"cluster_name":"Shared Autoscaling Americas","spark_version":"10.2.x-cpu-ml-scala2.12","node_type_id":"i3.2xl |
| mlflow_export_import.mlflow.databricks.cluster.libraries  | {"installable":[],"redacted":[]}                                                                               |
| mlflow_export_import.mlflow.databricks.notebook.commandID | 6101304639030907941_7207589773925520000_e458c0ed7c5c4e52b020b1b92d39b308                                       |
| mlflow_export_import.mlflow.databricks.notebookID         | 3532228                                                                                                        |
| mlflow_export_import.mlflow.databricks.notebookPath       | /Users/andre@mycompany.com/mlflow/02a_Sklearn_Train_Predict    |
| mlflow_export_import.mlflow.databricks.notebookRevisionID | 1647395473565                                                                                                  |
| mlflow_export_import.mlflow.databricks.webappURL          | https://demo.cloud.databricks.com                                                                              |
| mlflow_export_import.mlflow.log-model.history             | [{"artifact_path":"sklearn-model","signature":{"inputs":"[{\"name\": \"fixed acidity\", \"type\": \"double\"}, |
| mlflow_export_import.mlflow.runName                       | sklearn                                                                                                        |
| mlflow_export_import.mlflow.source.name                   | /Users/andre@mycompany.com/mlflow/02a_Sklearn_Train_Predict    |
| mlflow_export_import.mlflow.source.type                   | NOTEBOOK                                                                                                       |
| mlflow_export_import.mlflow.user                          | andre@mycompany.com                                                                                 |

#### MLflow RunInfo tags

|Tag | Value | 
|----|-------|
| mlflow_export_import.run_info.artifact_uri                | dbfs:/databricks/mlflow/3532228/826a19c33d8c461ebf91aa90c25a5dd8/artifacts |
| mlflow_export_import.run_info.end_time                    | 1647395473410                                                              |
| mlflow_export_import.run_info.experiment_id               | 3532228                                                                    |
| mlflow_export_import.run_info.lifecycle_stage             | active                                                                     |
| mlflow_export_import.run_info.run_id                      | 826a19c33d8c461ebf91aa90c25a5dd8                                           |
| mlflow_export_import.run_info.run_uuid                    | 826a19c33d8c461ebf91aa90c25a5dd8                                           |
| mlflow_export_import.run_info.start_time                  | 1647395462575                                                              |
| mlflow_export_import.run_info.status                      | FINISHED                                                                   |
| mlflow_export_import.run_info.user_id                     |                                                                            |

#### Metadata tags
|Tag | Value | 
|----|-------|
| mlflow_export_import.metadata.mlflow_version | 1.26.1 | 
| mlflow_export_import.metadata.tracking_uri                | databricks |
| mlflow_export_import.metadata.experiment_name             | /Users/andre@mycompany.com/mlflow/02a_Sklearn_Train_Predict    |
| mlflow_export_import.metadata.timestamp                   | 1655148303 |
| mlflow_export_import.metadata.timestamp_nice              | 2022-06-13 19:25:03 |

