
class ExportFields:
    """ Top-level fields for JSON export format. """
    SYSTEM = "system"
    INFO = "info"
    MLFLOW = "mlflow"


class ExportTags:
    """ Source export tags prefixes. """
    PREFIX_ROOT    = "mlflow_exim"
    PREFIX_FIELD = f"{PREFIX_ROOT}.field"
    PREFIX_RUN_INFO = f"{PREFIX_ROOT}.run_info"
    PREFIX_MLFLOW_TAG = f"{PREFIX_ROOT}.mlflow_tag"


def fmt_timestamps(tag, dct, tags):
    from mlflow_export_import.common import timestamp_utils
    ts = dct[tag]
    tags[f"{ExportTags.PREFIX_FIELD}.{tag}"] = str(ts)
    tags[f"{ExportTags.PREFIX_FIELD}._{tag}"] = timestamp_utils.fmt_ts_millis(ts, True)


def set_source_tags_for_field(dct, tags):
    """"
    Add an object's fields as source tags.
    """
    for k,v in dct.items():
        if k != "tags":
            tags[f"{ExportTags.PREFIX_FIELD}.{k}"] = str(v)


def mk_source_tags_mlflow_tag(tags):
    """"
    Create 'mlflow_.exim.mlflow_tag' source tags from 'mlflow' tags..
    """
    prefix = "mlflow."
    return { f"{ExportTags.PREFIX_MLFLOW_TAG}.{k.replace(prefix,'')}":str(v) for k,v in tags.items() if k.startswith(prefix) }


def mk_source_tags(tags, dst_prefix):
    """"
    Create source tags from destination prefix.
    """
    return { f"{dst_prefix}.{k}":str(v) for k,v in tags.items() }
