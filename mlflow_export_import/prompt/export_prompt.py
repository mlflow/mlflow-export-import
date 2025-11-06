"""
Exports MLflow prompts to a directory.

Note: This implementation uses standard MLflow APIs (mlflow.genai.*) with fallbacks 
for different MLflow versions to ensure compatibility across various deployments.
"""

import os
import click
import mlflow
from mlflow.exceptions import RestException

from mlflow_export_import.common import utils, io_utils
from mlflow_export_import.common.click_options import opt_output_dir
from mlflow_export_import.common.timestamp_utils import adjust_timestamps
from mlflow_export_import.common.version_utils import has_prompt_support, log_version_info
from mlflow_export_import.client.client_utils import create_mlflow_client

_logger = utils.getLogger(__name__)


def export_prompt(
        prompt_name,
        prompt_version,
        output_dir,
        mlflow_client=None
    ):
    """
    Export a single prompt version to a directory.
    
    :param prompt_name: Name of the prompt to export.
    :param prompt_version: Version of the prompt to export.
    :param output_dir: Output directory.
    :param mlflow_client: MLflow client.
    :return: Prompt object or None if export failed.
    """
    
    if not has_prompt_support():
        raise Exception(f"Prompt registry not supported in MLflow {mlflow.__version__} (requires 2.21.0+)")
    
    mlflow_client = mlflow_client or create_mlflow_client()
    log_version_info()
    
    try:
        # Get the prompt - handle both v2.21+ and v3.0+ API locations
        prompt = _get_prompt_safe(prompt_name, prompt_version)
        
        _logger.info(f"Exporting prompt: {prompt_name} version {prompt_version}")
        
        # Prepare prompt data for export - extract only serializable attributes
        prompt_info = {
            "name": prompt.name,
            "version": prompt.version,
            "template": prompt.template,
            "tags": dict(prompt.tags) if prompt.tags else {},
            "creation_timestamp": prompt.creation_timestamp,
            "last_updated_timestamp": prompt.last_updated_timestamp,
            "user_id": getattr(prompt, 'user_id', None),
            "description": getattr(prompt, 'description', None),
            "commit_message": getattr(prompt, 'commit_message', None),
            "variables": getattr(prompt, 'variables', None),
            "uri": getattr(prompt, 'uri', None)
        }
        
        # Convert any sets to lists for JSON serialization
        for key, value in prompt_info.items():
            if isinstance(value, set):
                prompt_info[key] = list(value)
        
        adjust_timestamps(prompt_info, ["creation_timestamp", "last_updated_timestamp"])
        
        mlflow_attr = {
            "prompt": prompt_info
        }
        
        # Write prompt export file
        io_utils.write_export_file(output_dir, "prompt.json", __file__, mlflow_attr)
        
        _logger.info(f"Successfully exported prompt: {prompt_name} version {prompt_version}")
        return prompt
        
    except RestException as e:
        _logger.error(f"Prompt export failed: {{'prompt_name': '{prompt_name}', 'version': '{prompt_version}', 'RestException': {e.json}}}")
        return None
    except Exception as e:
        _logger.error(f"Prompt export failed: {{'prompt_name': '{prompt_name}', 'version': '{prompt_version}', 'Exception': {str(e)}}}")
        return None


def _get_prompt_safe(prompt_name, prompt_version):
    """
    Get prompt version with compatibility across MLflow versions (2.21+ and 3.0+).
    """
    # Try MLflow 3.0+ genai namespace first
    try:
        import mlflow.genai
        if hasattr(mlflow.genai, 'load_prompt'):
            return mlflow.genai.load_prompt(prompt_name, prompt_version)
    except (ImportError, AttributeError):
        # Only catch import/attribute errors, not runtime errors like "prompt not found"
        pass
    
    # Try MLflow client approach (works with 2.21+)
    try:
        client = mlflow.MlflowClient()
        if hasattr(client, 'get_prompt_version'):
            return client.get_prompt_version(prompt_name, prompt_version)
    except (ImportError, AttributeError):
        pass
    
    # Try top-level functions (deprecated but may work)
    try:
        if hasattr(mlflow, 'load_prompt'):
            return mlflow.load_prompt(prompt_name, prompt_version)
    except (ImportError, AttributeError):
        pass
    
    raise Exception(f"No compatible prompt loading API found in MLflow {mlflow.__version__}. Ensure prompt registry is supported.")


@click.command()
@click.option("--prompt-name",
    help="Name of the prompt to export.",
    type=str,
    required=True
)
@click.option("--prompt-version",
    help="Version of the prompt to export.",
    type=str,
    required=True
)
@opt_output_dir
def main(prompt_name, prompt_version, output_dir):
    _logger.info("Options:")
    for k, v in locals().items():
        _logger.info(f"  {k}: {v}")
    
    export_prompt(
        prompt_name=prompt_name,
        prompt_version=prompt_version,
        output_dir=output_dir
    )


if __name__ == "__main__":
    main()