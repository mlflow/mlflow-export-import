
# ===========================================================
#
# Script to run tests against a source and destination MLflow tracking server.
# Expects the source and destination server port numbers as arguments.
#
# Does the following:
#  1. Launches a source and destination tracking server in the background.
#  2. Runs tests against the tracking servers with pytest.
#  3. Kills the tracking servers.
#
# Example:
#
#  run_tests.sh 5010 5011
#
# ===========================================================

if [ $# -lt 2 ] ; then
  echo "ERROR: Expecting source and destination MLflow Tracking Server ports"
  exit 1
  fi
PORT_SRC=$1
PORT_DST=$2

export MLFLOW_TRACKING_URI=http://localhost:$PORT_SRC
export MLFLOW_TRACKING_URI_SRC=http://localhost:${PORT_SRC}
export MLFLOW_TRACKING_URI_DST=http://localhost:${PORT_DST}

JUNIT_FILE=run_tests_junit.xml
HTML_FILE=run_tests_report.html
LOG_FILE=run_tests.log

message() {
  echo 
  echo "******************************************************"
  echo "*"
  echo "* $*"
  echo "*"
  echo "******************************************************"
  echo 
}

run_tests() {
  message "STAGE 2: RUN TESTS"
  time -p pytest -s \
    --junitxml=$JUNIT_FILE \
    --html=$HTML_FILE \
    --self-contained-html \
  test_*.py
}

launch_server() {
  port=$1
  message "STAGE 1: LAUNCH TRACKING SERVER on port $port"
  rm mlflow_${port}.db
  rm -rf mlruns_${port}
  mlflow server \
    --host localhost --port ${port}  \
    --backend-store-uri sqlite:///mlflow_${port}.db \
    --default-artifact-root $PWD/mlruns_${port}
}

kill_server() {
  port=$1
  message "STAGE 3: KILL TRACKING SERVER on port ${port}"
  echo "Killing MLflow Tracking Server pids:"
  pids=`lsof -n -i :${port} | awk '{ print ( $2 ) }' | grep -v PID`
  for pid in $pids ; do
    echo "  Killing PID=$pid"
    kill $pid
    done
  rm -rf mlruns_${port}
  rm  mlflow_${port}.db
}

run() {
  echo "$0: MLFLOW_TRACKING_URI: $MLFLOW_TRACKING_URI"
  launch_server $PORT_SRC &
  launch_server $PORT_DST &
  sleep 5 # wait for the tracking servers to come up
  run_tests
  kill_server $PORT_SRC
  kill_server $PORT_DST
}

run_all() {
  time -p run
  echo
  echo "******************************************************"
  echo
  echo "LOG_FILE    : $LOG_FILE"
  echo "JUNIT REPORT: $JUNIT_FILE"
  echo "HTML REPORT : $HTML_FILE"
  echo
}

time run_all 2>&1 | tee run_tests.log

exit 0
