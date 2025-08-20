import os
import yaml
import logging.config
from mlflow_export_import.bulk import config    #birbal added
log_path=config.log_path    #birbal added

_have_loaded_logging_config = False

def get_logger(name):
    global _have_loaded_logging_config
    if _have_loaded_logging_config:
        return logging.getLogger(name)

    config_path = os.environ.get("MLFLOW_EXPORT_IMPORT_LOG_CONFIG_FILE", None)
    output_path = os.environ.get("MLFLOW_EXPORT_IMPORT_LOG_OUTPUT_FILE", log_path)
    log_format = os.environ.get("MLFLOW_EXPORT_IMPORT_LOG_FORMAT", "%(asctime)s - %(levelname)s - [%(name)s:%(lineno)d] - %(message)s") #birbal updated


    #print(f"logging_utils.get_logger: config_path: {config_path}")
    #print(f"logging_utils.get_logger: output_path: {output_path}")
    #print(f"logging_utils.get_logger: log_format: {log_format}")

    if config_path:
        if not config_path.endswith(".yaml"):
            _load_default_log_config(output_path, log_format)
            logging.warning(f"Logging config file '{config_path}' must be .yaml file.")
        elif not os.path.exists(config_path):
            _load_default_log_config(output_path, log_format)
            logging.warning(f"Logging config file '{config_path}' does not exist.")
        else:
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f.read())
                logging.config.dictConfig(cfg)
            logging.info(f"Reading log config file '{config_path}'")
    else:
        _load_default_log_config(output_path, log_format)

    _have_loaded_logging_config = True
    return logging.getLogger(name)


def _load_default_log_config(output_path=None, log_format=None):
    cfg = _create_default_log_config(output_path, log_format)
    logging.config.dictConfig(cfg)
    msg = f"with output log file '{output_path}'" if output_path else "without output log file"
    logging.info(f"Using default logging config {msg}")


def _create_default_log_config(output_path=None, log_format=None):
    from mlflow_export_import.common.default_logging_config import config
    cfg = config.copy()
    if log_format:
        cfg["formatters"]["simple"]["format"] = log_format

    if output_path:
        file_handler = cfg["handlers"]["file"]
        file_handler["filename"] = output_path
    else:
        handlers = cfg["root"]["handlers"]
        handlers.remove("file")

    return cfg
