"""
Logged model utilities.
"""

from mlflow_export_import.common import utils

_logger = utils.getLogger(__name__)

def logged_model_to_json(logged_model):
    """
    Converts a logged model into a JSON string.
    """
    result = {}
    for k, v in utils.strip_underscores(logged_model).items():
        if hasattr(v, 'value'):
            # Handles enums like Status
            result[k] = v.value
        elif isinstance(v, list):
            # Handles metrics List data
            result[k] = [utils.strip_underscores(item) if hasattr(item, '__dict__') else item for item in v]
        elif hasattr(v, '__dict__'):
            result[k] = utils.strip_underscores(v)
        else:
            result[k] = v
    return result

