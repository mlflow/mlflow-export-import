# Mlflow Export Import - Databricks Tests

## Overview

Remote tests using the Databricks MLflow REST API.

## Setup

Configuration is simple. 
Copy [config.yaml.template](config.yaml.template) to `config.yaml` and adjust.

For both source and destination workspaces, set the following attributes:

* profile - Databricks profile
* base_dir - Workspace base directory where all test experiments will be created.


```
workspace_src:
  profile: databricks://ws_src_profile
  base_dir: /tmp/test-mlflow-expot-import

workspace_dst:
  profile: databricks://ws_dst_profile
  base_dir: /tmp/test-mlflow-expot-import
```

The `base_dir` folder will be deleted before each test session.

## Run tests

```
python -u -m pytest -s test_*.py
```

The script [run_tests.sh](run_tests.sh) is provided as a convenience.

## Debug

If the environment variable `MLFLOW_EXPORT_IMPORT_OUTPUT_DIR` is set, 
it will be used as the test directory instead of `tempfile.TemporaryDirectory()`.
