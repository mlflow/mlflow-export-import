"""
Prompt utilities.
"""

import time
from mlflow.exceptions import RestException

from mlflow_export_import.common import utils

_logger = utils.getLogger(__name__)


def delete_prompt(client, prompt_name, sleep_time=0.5):
    """
    Delete a prompt and all its versions.
    
    :param client: MLflow client
    :param prompt_name: Name of the prompt to delete
    :param sleep_time: Time to sleep between version deletions (default 0.5s, shorter than models since prompts don't have stage transitions)
    """
    try:
        _logger.info(f"Deleting prompt '{prompt_name}' and its versions")
        
        # Get all versions of the prompt
        try:
            versions = client.search_prompt_versions(prompt_name)
        except Exception:
            # Fallback: try to get versions by iterating
            versions = []
            version = 1
            while True:
                try:
                    pv = client.get_prompt_version(prompt_name, str(version))
                    versions.append(pv)
                    version += 1
                except Exception:
                    break
        
        # Delete all versions
        for pv in versions:
            _logger.info(f"  Deleting prompt version: {prompt_name} v{pv.version}")
            try:
                client.delete_prompt_version(prompt_name, str(pv.version))
                time.sleep(sleep_time)
            except Exception as e:
                _logger.warning(f"  Failed to delete version {pv.version}: {e}")
        
        # Delete the prompt itself
        try:
            client.delete_prompt(prompt_name)
            _logger.info(f"Deleted prompt '{prompt_name}'")
        except Exception as e:
            _logger.warning(f"Failed to delete prompt '{prompt_name}': {e}")
            
    except RestException:
        pass
    except Exception as e:
        _logger.warning(f"Error deleting prompt '{prompt_name}': {e}")
