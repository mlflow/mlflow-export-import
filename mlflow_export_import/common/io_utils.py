import os
import json

from mlflow_export_import.common.timestamp_utils import ts_now_seconds, ts_now_fmt_utc
from mlflow_export_import.common import filesystem as _filesystem
from mlflow_export_import.common.source_tags import ExportFields


def _mk_export_info():
    """
    Create common standard JSON stanza containing internal export information.
    """
    import mlflow
    import platform
    return {
        ExportFields.SYSTEM: {
            "export_time": ts_now_seconds,
            "_export_time": ts_now_fmt_utc,
            "mlflow_version": mlflow.__version__,
            "mlflow_tracking_uri": mlflow.get_tracking_uri(),
            "user": os.getlogin(),
            "platform": {
                "python_version": platform.python_version(),
                "system": platform.system()
            }
        }
    }


def write_export_file(dir, file, content, custom_info=None):
    """
    Write standard formatted JSON file.
    """
    path = os.path.join(dir, file)
    custom_info = { ExportFields.INFO: custom_info} if custom_info else {}
    content = { ExportFields.MLFLOW: content}
    content = { **_mk_export_info(), **custom_info, **content }
    os.makedirs(dir, exist_ok=True)
    write_file(path, content)


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


def get_custom(export_dct):
    return export_dct[ExportFields.INFO]


def get_mlflow(export_dct):
    return export_dct[ExportFields.MLFLOW]


def read_file_mlflow(path):
    dct = read_file(path)
    return dct[ExportFields.MLFLOW] 


def mk_manifest_json_path(input_dir, filename):
    return os.path.join(input_dir, filename)
