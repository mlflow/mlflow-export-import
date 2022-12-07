
class ExportTags:
    """ Tags for Run source export tags. """

    _TAG_PREFIX = "mlflow_export_import"
    TAG_PREFIX_RUN_INFO = f"{_TAG_PREFIX}.run_info"
    TAG_PREFIX_METADATA = f"{_TAG_PREFIX}.metadata"
    TAG_PREFIX_MLFLOW = f"{_TAG_PREFIX}.mlflow"

    TAG_EXPORT_TIME = "export_time"


class ImportTags:
    """ Tags for Registered Model and Version source import tags. """

    TAG_PREFIX = "mlflow_export_import.src"
    TAG_VERSION = f"{TAG_PREFIX}.version"


class MlflowTags:
    TAG_PREFIX = "mlflow."
    TAG_PARENT_ID = TAG_PREFIX + "parentRunId"
