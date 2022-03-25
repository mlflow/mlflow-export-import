# MLflow Export Import - Miscellanous Tools

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
