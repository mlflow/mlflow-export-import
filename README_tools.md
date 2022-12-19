# MLflow Export Import - Miscellanous Tools

## Download notebook with revision

This tool downloads a notebook with a specific revision.

Note that the parameter `revision_timestamp` which represents the revision ID to the API endpoint `workspace/export` is not publicly documented.

**Usage**
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

**Example**
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

**Usage**
```
http-client --help

Options:
  --api TEXT          API: mlflow|databricks.
  --resource TEXT     API resource such as 'experiments/list'.  [required]
  --method TEXT       HTTP method: GET|POST.
  --params TEXT       HTTP GET query parameters as JSON.
  --data TEXT         HTTP POST data as JSON.
  --output-file TEXT  Output file.
  --verbose BOOLEAN   Verbose.  [default: False]
```

**HTTP GET example**
```
export MLFLOW_TRACKING_URI=http://localhost:5000

http-client \
  --resource experiments/list\
  --output-file experiments.json
```

**HTTP POST example**
```
export MLFLOW_TRACKING_URI=http://localhost:5000

http-client \
  --resource experiments/create \
  --data '{"name": "my_experiment"}'
```
