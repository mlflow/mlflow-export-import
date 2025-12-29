"""
Imports MLflow prompts from a directory.

Note: This implementation uses standard MLflow APIs (mlflow.genai.*) with fallbacks 
for different MLflow versions to ensure compatibility across various deployments.
"""

import os
import json
import click
import mlflow
from mlflow.exceptions import RestException
from packaging import version

from mlflow_export_import.common import utils, io_utils
from mlflow_export_import.common.click_options import opt_input_dir
from mlflow_export_import.common.version_utils import has_prompt_support, log_version_info, get_mlflow_version, get_version_info
from mlflow_export_import.common.prompt_utils import delete_prompt as delete_prompt_util
from mlflow_export_import.client.client_utils import create_mlflow_client

_logger = utils.getLogger(__name__)


def _check_import_compatibility(prompt_data):
    """Check compatibility between source (exported) and target (current) MLflow versions."""
    
    # Get source version info from exported data
    system_info = prompt_data.get("system", {})
    source_version = system_info.get("mlflow_version", "unknown")
    source_tracking_uri = system_info.get("mlflow_tracking_uri", "unknown")
    
    # Get target version info
    target_version = str(get_mlflow_version())
    target_info = get_version_info()
    
    _logger.info(f"Version compatibility check:")
    _logger.info(f"  Source MLflow version: {source_version}")
    _logger.info(f"  Target MLflow version: {target_version}")
    _logger.info(f"  Source tracking URI: {source_tracking_uri}")
    
    # Check for potential compatibility issues
    try:
        source_ver = version.parse(source_version)
        target_ver = get_mlflow_version()
        
        # Check if target supports prompts
        if not target_info["supports_prompts"]:
            raise Exception(f"Target MLflow {target_version} does not support prompt registry (requires 2.21.0+)")
        
        # Warn about major version differences
        if source_ver.major != target_ver.major:
            _logger.warning(f"Major version difference detected: source v{source_ver.major} → target v{target_ver.major}")
            _logger.warning("Some features may not be fully compatible")
        
        # Check for specific compatibility issues
        if source_ver >= version.parse("3.0.0") and target_ver < version.parse("3.0.0"):
            _logger.warning("Importing from MLflow 3.x to 2.x - some metadata may be lost")
        
        _logger.info("Version compatibility check passed")
        
    except Exception as e:
        _logger.warning(f"Could not parse version information: {e}")
        _logger.info("Proceeding with import (version check inconclusive)")


def import_prompt(
        input_dir,
        prompt_name=None,
        delete_prompt=False,
        mlflow_client=None
    ):
    """
    Import a prompt from exported directory.
    
    :param input_dir: Input directory containing exported prompt.
    :param prompt_name: Optional new name for the imported prompt. If None, uses original name.
    :param delete_prompt: Delete existing prompt before importing.
    :param mlflow_client: MLflow client.
    :return: Imported prompt name and version or None if import failed.
    """
    
    if not has_prompt_support():
        raise Exception(f"Prompt registry not supported in MLflow {mlflow.__version__} (requires 2.21.0+)")
    
    mlflow_client = mlflow_client or create_mlflow_client()
    log_version_info()
    
    try:
        # Read exported prompt data
        prompt_path = os.path.join(input_dir, "prompt.json")
        if not os.path.exists(prompt_path):
            raise Exception(f"Prompt export file not found: {prompt_path}")
        
        # Read full export file for version compatibility check
        with open(prompt_path, 'r') as f:
            full_export_data = json.load(f)
        
        # Check version compatibility between source and target
        _check_import_compatibility(full_export_data)
        
        # Read MLflow-specific data for import
        prompt_data = io_utils.read_file_mlflow(prompt_path)
        
        _logger.info(f"Importing prompt from: {input_dir}")
        
        # Extract prompt information
        # read_file_mlflow returns the 'mlflow' section directly, so prompt data is at top level
        prompt_info = prompt_data.get("prompt", {})
        
        # Use provided name or original name
        final_prompt_name = prompt_name or prompt_info.get("name")
        if not final_prompt_name:
            raise Exception("No prompt name specified and none found in export data")
        
        # Delete existing prompt if requested
        if delete_prompt:
            delete_prompt_util(mlflow_client, final_prompt_name)
        
        # Create prompt in destination
        # Note: If prompt exists, register_prompt will fail - we catch this to preserve version numbers
        _logger.debug(f"Creating prompt '{final_prompt_name}' with template: {prompt_info.get('template', '')[:50]}...")
        try:
            imported_prompt = _create_prompt_safe(
                name=final_prompt_name,
                template=prompt_info.get("template", ""),
                tags=prompt_info.get("tags", {}),
                commit_message=prompt_info.get("commit_message"),
                mlflow_client=mlflow_client
            )
            
            if imported_prompt is None:
                _logger.error(f"Failed to create prompt '{final_prompt_name}' - _create_prompt_safe returned None")
                return None
                
        except Exception as e:
            error_msg = str(e)
            # Check if it's a duplicate error - skip to preserve version numbers
            if "already exists" in error_msg.lower() or "duplicate" in error_msg.lower() or "RESOURCE_ALREADY_EXISTS" in error_msg:
                _logger.warning(
                    f"Prompt '{final_prompt_name}' already exists - skipping import "
                    f"to preserve version numbers. Use --delete-prompt to replace."
                )
                return (final_prompt_name, None)
            else:
                # Re-raise if it's not a duplicate error
                raise
        
        _logger.info(f"Successfully imported prompt: {final_prompt_name}")
        return final_prompt_name, imported_prompt.version if hasattr(imported_prompt, 'version') else "1"
        
    except Exception as e:
        _logger.error(f"Prompt import failed: {str(e)}")
        return None


def _create_prompt_safe(name, template, tags=None, commit_message=None, mlflow_client=None):
    """
    Create prompt with compatibility across MLflow versions (2.21+ and 3.0+).
    """
    # Try MLflow 3.0+ genai namespace first
    try:
        import mlflow.genai
        if hasattr(mlflow.genai, 'register_prompt'):
            return mlflow.genai.register_prompt(
                name=name,
                template=template,
                tags=tags or {},
                commit_message=commit_message
            )
    except (ImportError, AttributeError) as e:
        _logger.debug(f"mlflow.genai.register_prompt not available: {e}")
    except Exception as e:
        _logger.debug(f"mlflow.genai.register_prompt failed: {e}")
    
    # Try MLflow client approach (works with 2.21+)
    try:
        client = mlflow_client or mlflow.MlflowClient()
        if hasattr(client, 'register_prompt'):
            return client.register_prompt(
                name=name,
                template=template,
                tags=tags or {},
                commit_message=commit_message
            )
    except (ImportError, AttributeError) as e:
        _logger.debug(f"client.register_prompt not available: {e}")
    except Exception as e:
        _logger.debug(f"client.register_prompt failed: {e}")
    
    # Try top-level functions (deprecated but may work)
    try:
        if hasattr(mlflow, 'register_prompt'):
            return mlflow.register_prompt(
                name=name,
                template=template,
                tags=tags or {},
                commit_message=commit_message
            )
    except (ImportError, AttributeError) as e:
        _logger.debug(f"mlflow.register_prompt not available: {e}")
    except Exception as e:
        _logger.debug(f"mlflow.register_prompt failed: {e}")
    
    raise Exception(f"No compatible prompt creation API found in MLflow {mlflow.__version__}. Ensure prompt registry is supported.")


@click.command()
@opt_input_dir
@click.option("--prompt-name",
    help="Optional new name for the imported prompt. If not specified, uses original name.",
    type=str,
    required=False
)
@click.option("--delete-prompt",
    help="Delete existing prompt before importing.",
    type=bool,
    default=False
)
def main(input_dir, prompt_name, delete_prompt):
    _logger.info("Options:")
    for k, v in locals().items():
        _logger.info(f"  {k}: {v}")
    
    import_prompt(
        input_dir=input_dir,
        prompt_name=prompt_name,
        delete_prompt=delete_prompt
    )


if __name__ == "__main__":
    main()