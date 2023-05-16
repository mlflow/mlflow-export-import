
export MLFLOW_TRACKING_URI=databricks

if [ $# -gt 0 ] ; then
  DATABRICKS_PROFILE=$1
  export MLFLOW_TRACKING_URI=databricks://$DATABRICKS_PROFILE
  fi

JUNIT_FILE=run_tests_junit.xml 
HTML_FILE=run_tests_report.html
LOG_FILE=run_tests.log

run() {
  echo "MLFLOW_TRACKING_URI: $MLFLOW_TRACKING_URI"
  time -p pytest -s \
    --junitxml=$JUNIT_FILE \
    --html=$HTML_FILE \
    --self-contained-html \
    --override-ini log_cli=true \
      `ls test_*.py`
  echo 
  echo "******************************************************"
  echo 
  echo "MLFLOW_TRACKING_URI: $MLFLOW_TRACKING_URI"
  echo "LOG_FILE    : $LOG_FILE"
  echo "JUNIT REPORT: $JUNIT_FILE"
  echo "HTML REPORT : $HTML_FILE"
  echo 
}

run | 2>&1 tee $LOG_FILE
