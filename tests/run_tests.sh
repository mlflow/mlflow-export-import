
# ===========================================================
#
# Script to run tests against a source and destination tracking server.
# Expects the source and destination server port numbers as an arguments.
#
# Does the following:
#  1. Launches an MLflow tracking server in the background
#  2. Runs tests against the server with pytest
#  3. Kills the MLflow tracking server
#
# Example:
#
#  run_tests.sh 5005 5006
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
  py.test -s test_*.py
  ##py.test -s test_bulk_experiments.py
}

launch_server() {
  port=$1
  message "STAGE 1: LAUNCH TRACKING SERVER"
  rm mlflow_${port}.db
  rm -rf mlruns_${port}
  mlflow server \
    --host localhost --port ${port}  \
    --backend-store-uri sqlite:///mlflow_${port}.db \
    --default-artifact-root $PWD/mlruns_${port}
}

kill_server() {
  port=$1
  message "STAGE 3: KILL TRACKING SERVER - PORT=${port}"
  echo "Killing MLflow Tracking Server pids:"
  pids=`lsof -n -i :${port} | awk '{ print ( $2 ) }' | grep -v PID`
  for pid in $pids ; do
    echo "  Killing PID=$pid"
    kill $pid
    done
}

run() {
  echo "$0: MLFLOW_TRACKING_URI: $MLFLOW_TRACKING_URI"
  launch_server $PORT_SRC &
  launch_server $PORT_DST &
  sleep 5
  run_tests
  kill_server $PORT_SRC
  kill_server $PORT_DST
}

run 2>&1 | tee run_tests.log

exit 0
