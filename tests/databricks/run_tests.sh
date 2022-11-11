
export PYTHONPATH=.:../..:..
export MLFLOW_TRACKING_URI=databricks

time -p python -u -m py.test -s --junitxml=test_junit.xml `ls tes*.py` | 2>&1 tee run_tests.log

