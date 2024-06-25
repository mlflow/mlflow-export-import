# MLflow Export Import - Tools

## Overview

* Some useful additional tools.
* See also [experimental tools](mlflow_export_import/tools/experimental/README.md).
* Last updated: _2024-06-24_.

## Model signature tools

These tools are useful for upgrading Databricks Workspace Registry models to Unity Catalog Registry models which require a model signature.

Model signature scripts:
* [get-model-signature](#get-model-signature)
* [set-model-signature](#set-model-signature)
* [list-model-versions-without-signatures](#list-model-versions-without-a-model-signature)

Test usage:
* [test_model_signature.py](tests/open_source/test_model_signature.py)

MLflow documentation: 
* [mlflow.models.set_signature](https://mlflow.org/docs/latest/python_api/mlflow.models.html#mlflow.models.set_signature)
* [Model Signatures And Input Examples](https://www.mlflow.org/docs/latest/models.html#model-signatures-and-input-examples)
* [MLflow Model Signatures and Input Examples Guide](https://www.mlflow.org/docs/latest/model/signatures.html)

### Get model signature

#### Overview
* Get the model signature of a model URI.
* Source: [get_model_signature.py](mlflow_export_import/tools/get_model_signature.py).

#### Run examples
```
get-model-signature \
  --model-uri models:/Sklearn_Wine/12 
```

```
get-model-signature \
  --model-uri runs:/73ab168e5775409fa3595157a415bb62/model
```

```
{
  "inputs": [
    {
      "type": "double",
      "name": "fixed_acidity",
      "required": true
    },
    {
    . . .
}
```

#### Options

```
get_model_signature --help

  Get the signature of an MLflow model.

Options:
  --model-uri TEXT    Model URI such as 'models:/my-model/3' or
                      'runs:/73ab168e5775409fa3595157a415bb62/my-model'.
                      [required]
  --output-file TEXT  Output file.
```

### Set model signature

#### Overview
* Set the model signature of a model URI.
* `models:/` scheme URIs are not accepted by [mlflow.models.set_signature](https://mlflow.org/docs/latest/python_api/mlflow.models.html#mlflow.models.set_signature) per documentation:
> model artifacts located in the model registry and represented by models:/ URI schemes are not compatible with this API
* For OSS MLflow, if you add a model signature to a run model, it will automatically update any model version that was created from that run. AFAIK this is not documented.
* Source: [set_model_signature.py](mlflow_export_import/tools/set_model_signature.py).


#### Run examples

```
set-model-signature \
  --model-uri runs:/73ab168e5775409fa3595157a415bb62/model \
  --input-file training_samples.csv \
  --output-file predictions_samples.csv
```

```
set-model-signature \
  --model-uri file:/run/model \
  --input-file training_samples.csv \
  --output-file predictions_samples.csv
```

#### Options
```
set-model-signature --help \

  Set the signature of an MLflow model.

Options:
  --model-uri TEXT               Model URI such as 'runs:/73ab168e5775409fa359
                                 5157a415bb62/my_model' or
                                 'file:/my_mlflow_model/.  Per MLflow
                                 documentation 'models:/' scheme is not
                                 supported.  [required]
  --input-file TEXT              Input CSV file with training data samples.
                                 [required]
  --output-file TEXT             Output CSV file with prediction data samples.
  --overwrite-signature BOOLEAN  Overwrite existing model signature.
```


### List model versions without a model signature

#### Overview
* List model versions without a model signature.
* Source: [list_model_versions_without_signatures.py](mlflow_export_import/tools/list_model_versions_without_signatures.py).

#### Run examples

```
list-model-versions-without-signatures \
  --output-file model-versions-without-signatures.csv
```

```
list-model-versions-without-signatures \
  --filter "name like 'sklearn%' \
  --output-file model-versions-without-signatures.csv
```

```
+------------------+-----------+----------------------------------+---------+
| model            |   version | run_id                           | error   |
|------------------|-----------|----------------------------------|---------|
| sklearn_iris     |         1 | de99a1259e7e47ebb3c701d13a7680b0 |         |
| sklearn_wine     |        27 | 4f6355ff885e4e158cdfbc5e77b47d33 |         |
| sklearn_wine     |        24 | 80a7b81527c2462abd168cb0f549a33b |         |
| sklearn_wine     |        18 | f8fca475b2cc4995b75b5a51236e1251 |         |
| tensorflow_mnist |        11 | d8d008e022504dc78cbc9799a9e5d3b3 |         |
| xgboost_wine     |         1 | 53292dc36dca423ebfb8a33667143a74 |         |
+------------------+-----------+----------------------------------+---------+
```

#### Options
```
list-model-versions-without-signatures --help

  List model versions without a model signature.

Options:
  --filter TEXT       For OSS MLflow this is a filter for
                      search_model_versions(), for Databricks it is for
                      search_registered_models() due to Databricks MLflow
                      search limitations.
  --output-file TEXT  Output file.
```


## Download notebook with revision

This tool downloads a notebook with a specific revision.

Note that the parameter `revision_timestamp` which represents the revision ID to the API endpoint `workspace/export` is not publicly documented.

##### Usage
```
download-notebook --help

Options:
  --output-dir TEXT        Output directory.  [required]
  --notebook TEXT          Notebook path.  [required]
  --revision TEXT          Notebook revision. If not specified will download
                           the latest revision.
  --notebook-formats TEXT  Databricks notebook formats. Values are SOURCE,
                           HTML, JUPYTER or DBC (comma seperated).  [default:
                           SOURCE]
```

##### Run examples
```
download-notebook \
  --output-dir out \
  --notebook /Users/andre@mycompany.com/mlflow/02a_Sklearn_Train_Predict \
  --revision 12345 \
  --notebook-formats SOURCE,DBC
```

```
ls -c1 out

02a_Sklearn_Train_Predict.dbc
02a_Sklearn_Train_Predict.source
```

## Call http_client - MLflow API or Databricks API

A convenience script to directly invoke either the MLflow API or Databricks API.

##### Usage
```
http-client --help

Options:
Options:
  --api TEXT          API: mlflow|databricks.
  --resource TEXT     API resource such as 'experiments/search'.  [required]
  --method TEXT       HTTP method: GET|POST|PUT|PATCH|DELETE.
  --params TEXT       HTTP GET query parameters as JSON.
  --data TEXT         HTTP request entity body as JSON (for POST, PUT and
                      PATCH).
  --output-file TEXT  Output file.
```

##### HTTP GET example
```
export MLFLOW_TRACKING_URI=http://localhost:5000

http-client \
  --resource experiments/list \
  --output-file experiments.json
```

##### HTTP GET example - Databricks API
```
http-client \
  --api databricks \
  --resource clusters/list \
  --output-file experiments.json
```

##### HTTP POST example
```
export MLFLOW_TRACKING_URI=http://localhost:5000

http-client \
  --resource experiments/create \
  --data '{"name": "my_experiment"}'
```


## Workflow API

* [README.md](mlflow_export_import/workflow_api/README.md)
* The `WorkflowApiClient` is a Python wrapper around the Databricks REST API to execute job runs in a synchronous polling manner.
* Although a generic tool, in terms of mlflow-export-import, its main use is for testing Databricks notebook jobs.


