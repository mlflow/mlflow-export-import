from importlib.metadata import version, PackageNotFoundError

pkg = "mlflow_export_import"

def get_version():
    try:
        return version(pkg)
    except PackageNotFoundError:
        return ""
