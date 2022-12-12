
class ExportFields:
    """ Fields for Run source export tags. """
    EXPORT_INFO = "export_info"
    CUSTOM_INFO = "custom_info"
    EXPORT_TIME = "export_time"

class ExportTags:
    PREFIX_ROOT    = "mlflow_export_import"
    PREFIX_RUN_INFO = f"{PREFIX_ROOT}.run_info"
