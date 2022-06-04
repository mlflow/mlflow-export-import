
# ===========================================================
#
# Script to run tests against a tracking server.
# Expects the server port number as an argument.
#
# Does the following:
#  1. Launches an MLflow tracking server in the background
#  2. Runs tests against the server with pytest
#  3. Kills the MLflow tracking server
#
# ===========================================================

if [ $# -lt 1 ] ; then
  echo "$0: Expecting MLflow Tracking Server port"
  exit 1
  fi
PORT=$1
export MLFLOW_TRACKING_URI=http://localhost:$PORT

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
  export PYTHONPATH=..:.
  rm -rf mlruns/*
  py.test -s test_*.py
}

launch_server() {
  message "STAGE 1: LAUNCH TRACKING SERVER"
  rm mlflow.db
  mlflow server \
    --host localhost --port $PORT  \
    --backend-store-uri sqlite:///mlflow.db \
    --default-artifact-root $PWD/mlruns
}

kill_server() {
  message "STAGE 3: KILL TRACKING SERVER"
  echo "Killing MLflow Tracking Server pids:"
  pids=`lsof -n -i :$PORT | awk '{ print ( $2 ) }' | grep -v PID`
  for pid in $pids ; do
    echo "  Killing PID=$pid"
    kill $pid
    done
}

run() {
  echo "$0: MLFLOW_TRACKING_URI: $MLFLOW_TRACKING_URI"
  launch_server &
  sleep 5
  run_tests
  kill_server
}

run 2>&1 | tee run_tests.log

exit 0
