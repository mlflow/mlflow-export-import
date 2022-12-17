
from importlib.metadata import version

pkg = "mlflow_export_import"

def get_version():
    return version(pkg)
