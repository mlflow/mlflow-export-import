# mlflow-export-import tests

## Notes

* The tests assume you have a MLflow tracking server running.
* TODO
  * Have two tracking servers running - one source and the other destination. 
Currently the tests suppport only one tracking server which complicates the test logic especially for the bulk tests.
  * Automatically launch the tracking servers when testing, be it with docker or like [github.com/mlflow/tests](https://github.com/mlflow/mlflow/tree/master/tests) does it.

## Setup

Virtual environment
```
conda env create conda.yaml
conda activate mlflow-export-import-tests
```

Launch a local MLflow tracking server

```
mlflow server --host localhost --port 5001 \
  --backend-store-uri sqlite:///mlflow.db \
  --default-artifact-root mlruns
```
  
## Run tests

```
export MLFLOW_TRACKING_URI=http://localhost:5001
export PYTHONPATH=..
pytest -s -v test*.py
```

```
======================= 33 passed, 4 warnings in 12.26s ========================
```


