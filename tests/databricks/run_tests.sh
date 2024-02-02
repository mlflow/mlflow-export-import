
run() {
  mlflow_version=`mlflow --version | sed -e "s/mlflow, version //" `
  echo "MLFLOW.VERSION: $mlflow_version"
  python -u -m pytest -s test_*.py
  echo "MLFLOW.VERSION: $mlflow_version"
}
run 2>&1 | tee run_tests.log
