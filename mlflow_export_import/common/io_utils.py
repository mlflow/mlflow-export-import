import os
import json

from mlflow_export_import.common.timestamp_utils import ts_now_seconds, ts_now_fmt_local, ts_now_fmt_utc
from mlflow_export_import.common import filesystem as _filesystem
from mlflow_export_import.common.source_tags import ExportTags


def write_json_file(fs, path, dct):
    fs.write(path, json.dumps(dct,indent=2)+"\n")


def _mk_export_info():
    import mlflow
    import platform
    return {
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

def _create_create_export_info(my_info=None):
    info = _mk_export_info()
    if my_info:
        info = { **info, **my_info }
    return { "export_info": info }


def write_json(output_dir, file, dct, my_info=None):
    path = os.path.join(output_dir, file)
    info = _create_create_export_info(my_info)
    dct = { **info, **dct }
    fs = _filesystem.get_filesystem(output_dir)
    fs.mkdirs(output_dir)
    write_json_file(fs, path, dct)
    return fs


def write_file(path, content):
    with open(_filesystem.mk_local_path(path), "wb" ) as f:
        f.write(content)


def read_json_file(path):
    with open(_filesystem.mk_local_path(path), "r", encoding="utf-8") as f:
        return json.loads(f.read())


def mk_manifest_json_path(input_dir, filename):
    """ Handle depcrecated "manifest.json" instead of current MLflow object file name such as "experiments.json". Former file name will be eventually removed. """
    path = os.path.join(input_dir, filename)
    if not os.path.exists(path):
        path = os.path.join(input_dir, "manifest.json") # NOTE: old deprecated, will be eventually removed
    return path
