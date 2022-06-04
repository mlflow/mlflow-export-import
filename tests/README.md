# mlflow-export-import tests

## Setup

Virtual environment
```
conda env create conda.yaml
conda activate mlflow-export-import-tests
```
  
## Run tests

To run the tests use the [run_tests.sh](run_tests.sh) script and specify the port number.
The script does the following:
* Launches an MLflow tracking server in the background
* Runs tests against this server with pytest
* Kills the MLflow tracking server

**Example**
```
run_tests.sh 5005
```
```
======================== 38 passed in 295.36s (0:04:55) ========================

```
