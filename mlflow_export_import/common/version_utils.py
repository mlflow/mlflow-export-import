"""
MLflow version detection and compatibility utilities.
"""

import mlflow
from packaging import version
from mlflow_export_import.common import utils

_logger = utils.getLogger(__name__)


def get_mlflow_version():
    """Get the current MLflow version as a packaging.version.Version object."""
    return version.parse(mlflow.__version__)


# MLflow Features (relevant for export/import)
def has_trace_support():
    """Tracing system - traces and spans data (2.14.0+)."""
    return get_mlflow_version() >= version.parse("2.14.0")


def has_prompt_support():
    """Prompt registry - versioned prompts and templates (2.21.0+)."""
    return get_mlflow_version() >= version.parse("2.21.0")


def has_logged_model_support():
    """LoggedModel entity - first-class model objects (3.0.0+)."""
    return get_mlflow_version() >= version.parse("3.0.0")

def has_assessments_support():
    """Assessments entity - first-class model objects (3.2.0+)."""
    return get_mlflow_version() >= version.parse("3.2.0")

def has_evaluation_dataset_support():
    """Evaluation datasets stored in experiments (3.4.0+)."""
    return get_mlflow_version() >= version.parse("3.4.0")


def get_version_info():
    """Get comprehensive version and feature support information."""
    return {
        "mlflow_version": str(get_mlflow_version()),
        "supports_traces": has_trace_support(),
        "supports_prompts": has_prompt_support(),
        "supports_logged_models": has_logged_model_support(),
        "supports_evaluation_datasets": has_evaluation_dataset_support()
    }


def log_version_info():
    """Log version information for debugging."""
    info = get_version_info()
    _logger.info(f"MLflow version: {info['mlflow_version']}")
    _logger.info(f"Feature support: traces={info['supports_traces']}, prompts={info['supports_prompts']}, "
                 f"logged_models={info['supports_logged_models']}, evaluation_datasets={info['supports_evaluation_datasets']}")


