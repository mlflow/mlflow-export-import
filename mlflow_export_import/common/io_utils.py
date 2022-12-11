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

ATTR_CUSTOM_INFO = "custom_info"

def write_manifest_file(dir, file, content, custom_info=None):
    """
    Write standard manifest JSON file with 'export_info' stanza.
    """
    path = os.path.join(dir, file)
    custom_info = { ATTR_CUSTOM_INFO: custom_info} if custom_info else {}
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


def mk_manifest_json_path(input_dir, filename):
    return os.path.join(input_dir, filename)
