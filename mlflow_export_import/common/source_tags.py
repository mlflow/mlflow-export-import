
class ExportFields:
    """ Fields for JSON export format. """
    SYSTEM = "system"
    INFO = "info"
    MLFLOW = "mlflow"


class ExportTags:
    """ Tags source export tags. """
    PREFIX_ROOT    = "mlflow_exim"
    PREFIX_RUN_INFO = f"{PREFIX_ROOT}.run_info"
    PREFIX_MLFLOW = f"{PREFIX_ROOT}.mlflow"
    PREFIX_FIELD = f"{PREFIX_ROOT}.field"
    PREFIX_TAG = f"{PREFIX_ROOT}.tag"
