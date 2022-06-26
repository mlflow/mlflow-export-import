
export PYTHONPATH=.:../..:../open_source
export MLFLOW_TRACKING_URI=databricks

time -p python -u -m pytest -s `ls tes*.py` | 2>&1 tee run_tests.log
