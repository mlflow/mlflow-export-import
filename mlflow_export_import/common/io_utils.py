import os
import json

from mlflow_export_import.common.timestamp_utils import ts_now_seconds, ts_now_fmt_local, ts_now_fmt_utc
from mlflow_export_import.common import filesystem as _filesystem
from mlflow_export_import.common.source_tags import ExportTags


def _mk_export_info():
    """
    Create common standard manifest JSON stanza containing internal export information.
    """
    import mlflow
    import platform
    return {
        "export_info": {
            "mlflow_version": mlflow.__version__,
            "mlflow_tracking_uri": mlflow.get_tracking_uri(),
            "user": os.getlogin(),
            "platform": {
                "python_version": platform.python_version(),
                "system": platform.system()
            },
            ExportTags.TAG_EXPORT_TIME: {
                "seconds": ts_now_seconds,
                "local_time": ts_now_fmt_local,
                "utc_time": ts_now_fmt_utc
            }
        }
    }


def write_manifest_file(dir, file, dct):
    """
    Write standard manifest JSON file with 'export_info' stanza.
    """
    path = os.path.join(dir, file)
    dct = { **_mk_export_info(), **dct }
    os.makedirs(dir, exist_ok=True)
    write_file(path, dct)


def write_file(path, content):
    """
    Write a JSON or text file.
    """
    path = _filesystem.mk_local_path(path)
    if path.endswith(".json"):
        with open(path, "w", encoding="utf-8") as f:
            f.write(json.dumps(content, indent=2)+"\n")
    else:
        with open(path, "wb" ) as f:
            f.write(content)


def read_file(path):
    """
    Read a JSON or text file.
    """
    if path.endswith(".json"):
        with open(_filesystem.mk_local_path(path), "r", encoding="utf-8") as f:
            return json.loads(f.read())
    else:
        with open(_filesystem.mk_local_path(path), "r", encoding="utf-8") as f:
            return json.loads(f.read())


def mk_manifest_json_path(input_dir, filename):
    """ 
    Handle deprecated 'manifest.json' instead of current MLflow object file name such as 'experiments.json'. 
    'manifest.json' file name will be eventually removed. 
    """
    path = os.path.join(input_dir, filename)
    if not os.path.exists(path):
        path = os.path.join(input_dir, "manifest.json") # NOTE: old deprecated, will be eventually removed
    return path
