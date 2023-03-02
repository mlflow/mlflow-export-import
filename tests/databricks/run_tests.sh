
export PYTHONPATH=.:../..:..
export MLFLOW_TRACKING_URI=databricks

JUNIT_FILE=run_tests_junit.xml 
HTML_FILE=run_tests_report.html
LOG_FILE=run_tests.log

run() {
  time -p python -u -m pytest -s \
    --junitxml=$JUNIT_FILE \
    --html=$HTML_FILE \
    --self-contained-html \
    `ls test_*.py`

  echo 
  echo "******************************************************"
  echo 
  echo "LOG_FILE    : $LOG_FILE"
  echo "JUNIT REPORT: $JUNIT_FILE"
  echo "HTML REPORT : $HTML_FILE"
  echo 
}

run | 2>&1 tee $LOG_FILE
