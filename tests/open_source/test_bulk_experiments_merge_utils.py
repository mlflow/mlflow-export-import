from mlflow_export_import.bulk import experiments_merge_utils
import pytest


dct1 = {
  "system": {
    "package_version": "1.2.0",
    "script": "export_experiments.py",
    "export_time": 1683865840,
    "_export_time": "2023-05-12 04:30:40",
    "mlflow_version": "2.3.0",
    "mlflow_tracking_uri": "http://127.0.0.1:5020",
    "platform": {
      "python_version": "3.8.15",
      "system": "Darwin",
      "processor": "i386"
    },
    "user": "k2"
  },
  "info": {
    "experiment_names": [
      "sklearn_wine"
    ],
    "duration": 0.1,
    "experiments": 1,
    "total_runs": 1,
    "ok_runs": 1,
    "failed_runs": 0
  },
  "mlflow": {
    "experiments": [
      {
        "id": "1",
        "name": "sklearn_wine",
        "ok_runs": 3,
        "failed_runs": 1,
        "duration": 0.1
      }
    ]
  }
}


dct2 = {
  "system": {
    "package_version": "1.2.0",
    "script": "export_experiments.py",
    "export_time": 1683865840,
    "_export_time": "2023-05-12 04:30:40",
    "mlflow_version": "2.3.0",
    "mlflow_tracking_uri": "http://127.0.0.1:5020",
    "platform": {
      "python_version": "3.8.15",
      "system": "Darwin",
      "processor": "i386"
    },
    "user": "k2"
  },
  "info": {
    "experiment_names": [
      "Default"
    ],
    "duration": 0.2,
    "experiments": 1,
    "total_runs": 0,
    "ok_runs": 0,
    "failed_runs": 0
  },
  "mlflow": {
    "experiments": [
      {
        "id": "0",
        "name": "Default",
        "ok_runs": 0,
        "failed_runs": 0,
        "duration": 0.0
      }
    ]
  }
}


def test_merge_info():
    info1 = dct1["info"]
    info2 = dct2["info"]
    info = experiments_merge_utils.merge_info(info1, info2)
    assert info["duration"] == pytest.approx(info1["duration"] + info2["duration"])
    assert info["total_runs"] == info1["total_runs"] + info2["total_runs"]
    assert info["ok_runs"] == info1["ok_runs"] + info2["ok_runs"]
    assert info["failed_runs"] == info1["failed_runs"] + info2["failed_runs"]
    assert info["experiments"] == info1["experiments"] + info2["experiments"]


def test_merge_mlflow():
    mlflow1 = dct1["mlflow"]
    mlflow2 = dct2["mlflow"]
    mlflow = experiments_merge_utils.merge_mlflow(mlflow1, mlflow2)

    assert len(mlflow["experiments"]) == len(mlflow1["experiments"])  + len(mlflow2["experiments"])
    assert mlflow["experiments"] == mlflow1["experiments"]  + mlflow2["experiments"] 
