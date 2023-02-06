import os
import getpass
import json
import yaml

from mlflow_export_import.common.timestamp_utils import ts_now_seconds, ts_now_fmt_utc
from mlflow_export_import.common import filesystem as _filesystem
from mlflow_export_import.common.source_tags import ExportFields
from mlflow_export_import.common.pkg_version import get_version #


def _mk_system_attr(script):
    """
    Create common standard JSON stanza containing internal export information.
    """
    import mlflow
    import platform
    return {
        ExportFields.SYSTEM: {
            "package_version": get_version(),
            "script": os.path.basename(script),
            "export_time": ts_now_seconds,
            "_export_time": ts_now_fmt_utc,
            "mlflow_version": mlflow.__version__,
            "mlflow_tracking_uri": mlflow.get_tracking_uri(),
            "user": getpass.getuser(),
            "platform": {
                "python_version": platform.python_version(),
                "system": platform.system()
            }
        }
    }


def write_export_file(dir, file, script, mlflow_attr, info_attr=None):
    """
    Write standard formatted JSON file.
    """
    dir = _filesystem.mk_local_path(dir)
    path = os.path.join(dir, file)
    info_attr = { ExportFields.INFO: info_attr} if info_attr else {}
    mlflow_attr = { ExportFields.MLFLOW: mlflow_attr}
    mlflow_attr = { **_mk_system_attr(script), **info_attr, **mlflow_attr }
    os.makedirs(dir, exist_ok=True)
    write_file(path, mlflow_attr)


def _is_yaml(path, file_type=None):
    return any(path.endswith(x) for x in [".yaml",".yml"]) or file_type in ["yaml","yml"]


def write_file(path, content, file_type=None):
    """
    Write to JSON, YAML or text file.
    """
    path = _filesystem.mk_local_path(path)
    if path.endswith(".json"):
        with open(path, "w", encoding="utf-8") as f:
            f.write(json.dumps(content, indent=2)+"\n")
    elif _is_yaml(path, file_type):
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(content, f)
    else:
        with open(path, "wb" ) as f:
            f.write(content)


def read_file(path, file_type=None):
    """
    Read a JSON, YAML or text file.
    """
    with open(_filesystem.mk_local_path(path), "r", encoding="utf-8") as f:
        if path.endswith(".json"):
            return json.loads(f.read())
        elif _is_yaml(path, file_type):
            return yaml.safe_load(f)
        else:
            return f.read()


def get_info(export_dct):
    return export_dct[ExportFields.INFO]


def get_mlflow(export_dct):
    return export_dct[ExportFields.MLFLOW]


def read_file_mlflow(path):
    dct = read_file(path)
    return dct[ExportFields.MLFLOW] 


def mk_manifest_json_path(input_dir, filename):
    return os.path.join(input_dir, filename)
