"""
Exports multiple MLflow prompts to a directory.

Note: This implementation uses standard MLflow APIs that are available across different
MLflow deployments. Version discovery is done by iteratively checking version numbers 
1-10 to ensure compatibility with various MLflow configurations.
"""

import os
import click
import mlflow
from concurrent.futures import ThreadPoolExecutor

from mlflow_export_import.common import utils, io_utils
from mlflow_export_import.common.click_options import opt_output_dir
from mlflow_export_import.common.version_utils import has_prompt_support, log_version_info
from mlflow_export_import.client.client_utils import create_mlflow_client
from mlflow_export_import.prompt.export_prompt import export_prompt

_logger = utils.getLogger(__name__)


def export_prompts(
        output_dir,
        prompt_names=None,
        use_threads=False,
        mlflow_client=None
    ):
    """
    Export multiple prompts to a directory.
    
    :param output_dir: Output directory.
    :param prompt_names: List of prompt names to export. If None, exports all prompts.
    :param use_threads: Use multithreading for export.
    :param mlflow_client: MLflow client.
    :return: Summary of export results.
    """
    
    if not has_prompt_support():
        raise Exception(f"Prompt registry not supported in MLflow {mlflow.__version__} (requires 2.21.0+)")
    
    mlflow_client = mlflow_client or create_mlflow_client()
    log_version_info()
    
    try:
        # Get list of prompts to export
        if prompt_names:
            prompts_to_export = _get_specified_prompts(prompt_names)
        else:
            prompts_to_export = _get_all_prompt_versions()
        
        _logger.info(f"Found {len(prompts_to_export)} prompts to export")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Export prompts
        if use_threads:
            results = _export_prompts_threaded(prompts_to_export, output_dir)
        else:
            results = _export_prompts_sequential(prompts_to_export, output_dir)
        
        # Summary
        successful = [r for r in results if r is not None]
        failed = len(results) - len(successful)
        
        summary = {
            "total_prompts": len(prompts_to_export),
            "successful_exports": len(successful),
            "failed_exports": failed
        }
        
        # Write summary
        io_utils.write_export_file(output_dir, "prompts_summary.json", __file__, summary)
        
        _logger.info(f"Prompt export completed: {summary}")
        return summary
        
    except Exception as e:
        _logger.error(f"Bulk prompt export failed: {str(e)}")
        return None


def _get_all_prompts():
    """Get all available prompts from the registry using standard MLflow APIs."""
    
    # Try MLflow 3.0+ genai namespace first (recommended standard API)
    try:
        import mlflow.genai
        if hasattr(mlflow.genai, 'search_prompts'):
            return mlflow.genai.search_prompts()
    except (ImportError, AttributeError, Exception):
        pass
    
    # Try top-level functions (deprecated but may work)
    try:
        if hasattr(mlflow, 'search_prompts'):
            return mlflow.search_prompts()
    except (ImportError, AttributeError, Exception):
        pass
    
    # Try MLflow client approach
    try:
        client = mlflow.MlflowClient()
        if hasattr(client, 'search_prompts'):
            return client.search_prompts()
    except (ImportError, AttributeError, Exception):
        pass
    
    raise Exception(f"No compatible prompt search API found in MLflow {mlflow.__version__}. Ensure prompt registry is supported.")


def _get_all_prompt_versions():
    """Get all prompt versions from all prompts."""
    all_prompts = _get_all_prompts()
    prompt_versions = []
    
    for prompt in all_prompts:
        versions = _get_prompt_versions(prompt.name)
        prompt_versions.extend(versions)
    
    return prompt_versions


def _get_prompt_versions(prompt_name):
    """Get all versions of a specific prompt using best available API."""
    from mlflow_export_import.prompt.export_prompt import _get_prompt_safe
    
    # Try search_prompt_versions API first (MLflow 3.0+, Unity Catalog)
    # This is the proper way to get all versions without iteration
    try:
        client = mlflow.MlflowClient()
        if hasattr(client, 'search_prompt_versions'):
            _logger.debug(f"Using search_prompt_versions API for '{prompt_name}'")
            response = client.search_prompt_versions(prompt_name, max_results=1000)
            versions = list(response.prompt_versions) if hasattr(response, 'prompt_versions') else list(response)
            if versions:
                # Sort by version number to ensure consistent ordering (important for version preservation)
                versions = sorted(versions, key=lambda v: int(v.version))
                _logger.info(f"Found {len(versions)} version(s) for prompt '{prompt_name}' via search API")
                return versions
    except Exception as e:
        _logger.debug(f"search_prompt_versions not available or failed: {e}")
    
    # Fallback: iterative discovery for OSS MLflow or older versions
    # This approach works across different MLflow deployments but has limitations
    _logger.debug(f"Using iterative version discovery for '{prompt_name}'")
    versions = []
    
    # Try versions 1-100 (increased from 10 to handle more versions)
    # Stop early if we hit consecutive missing versions
    consecutive_missing = 0
    max_consecutive_missing = 3  # Stop after 3 consecutive missing versions
    
    for version_num in range(1, 101):
        try:
            prompt_version = _get_prompt_safe(prompt_name, str(version_num))
            versions.append(prompt_version)
            consecutive_missing = 0  # Reset counter on success
        except Exception:
            consecutive_missing += 1
            if consecutive_missing >= max_consecutive_missing:
                # Assume no more versions exist
                break
    
    if not versions:
        _logger.warning(f"No versions found for prompt '{prompt_name}'")
    else:
        _logger.info(f"Found {len(versions)} version(s) for prompt '{prompt_name}' via iteration")
    
    return versions


def _get_specified_prompts(prompt_names):
    """Get specified prompts with their latest versions."""
    prompts = []
    for prompt_name in prompt_names:
        try:
            # Get the prompt and find its latest version
            prompt_versions = _get_prompt_versions(prompt_name)
            if prompt_versions:
                # Get the latest version
                latest = max(prompt_versions, key=lambda x: int(x.version))
                prompts.append(latest)
            else:
                _logger.warning(f"Prompt '{prompt_name}' not found")
        except Exception as e:
            _logger.error(f"Error getting prompt '{prompt_name}': {e}")
    
    return prompts


def _export_prompts_sequential(prompts, output_dir):
    """Export prompts sequentially."""
    results = []
    for prompt in prompts:
        prompt_dir = os.path.join(output_dir, f"{prompt.name}_v{prompt.version}")
        result = export_prompt(prompt.name, prompt.version, prompt_dir)
        results.append(result)
    return results


def _export_prompts_threaded(prompts, output_dir):
    """Export prompts using multithreading."""
    def export_single(prompt):
        prompt_dir = os.path.join(output_dir, f"{prompt.name}_v{prompt.version}")
        return export_prompt(prompt.name, prompt.version, prompt_dir)
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(export_single, prompts))
    
    return results


@click.command()
@opt_output_dir
@click.option("--prompt-names",
    help="Comma-separated list of prompt names to export. If not specified, exports all prompts.",
    type=str,
    required=False
)
@click.option("--use-threads",
    help="Use multithreading for export.",
    is_flag=True,
    default=False
)
def main(output_dir, prompt_names, use_threads):
    _logger.info("Options:")
    for k, v in locals().items():
        _logger.info(f"  {k}: {v}")
    
    prompt_names_list = None
    if prompt_names:
        prompt_names_list = [name.strip() for name in prompt_names.split(",")]
    
    export_prompts(
        output_dir=output_dir,
        prompt_names=prompt_names_list,
        use_threads=use_threads
    )


if __name__ == "__main__":
    main()