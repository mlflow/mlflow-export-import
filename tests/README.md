# mlflow-export-import tests

## Setup

Virtual environment
```
conda env create conda.yaml
conda activate mlflow-export-import-tests
```
  
## Run tests

To run the tests use the [run_tests.sh](run_tests.sh) script and specify the source and destination tracking server port number 
The script does the following:
* Launches two MLflow tracking servers in the background - one for source and one for destination.
* Runs tests against these server with pytest.
* Kills the MLflow tracking servers.

**Example**
```
run_tests.sh 5005 5006
```
```
======================== 37 passed in 295.36s (0:04:55) ========================

```
