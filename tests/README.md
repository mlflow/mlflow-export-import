# mlflow-export-import tests

## Setup

```
conda env create conda.yaml
source activate mlflow-export-import-tests
```

  
## Run tests

### Start MLflow tracking server

```
mlflow server --host 0.0.0.0 --port 5000 \
  --backend-store-uri sqlite:///mlflow.db \
  --default-artifact-root $PWD/mlruns  
```

### Run tests
```
export MLFLOW_TRACKING_URI=http://localhost:5000
export PYTHONPATH=..
pytest -s -v test*.py
```
