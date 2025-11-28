"""
Imports multiple MLflow prompts from a directory.

Note: This implementation uses standard MLflow APIs (mlflow.genai.*) with fallbacks 
for different MLflow versions to ensure compatibility across various deployments.
"""

import os
import sys
import click
import mlflow
from concurrent.futures import ThreadPoolExecutor

from mlflow_export_import.common import utils, io_utils
from mlflow_export_import.common.click_options import opt_input_dir
from mlflow_export_import.common.version_utils import has_prompt_support, log_version_info
from mlflow_export_import.client.client_utils import create_mlflow_client
from mlflow_export_import.prompt.import_prompt import import_prompt

_logger = utils.getLogger(__name__)


def import_prompts(
        input_dir,
        delete_prompt=False,
        use_threads=False,
        mlflow_client=None
    ):
    """
    Import multiple prompts from a directory.
    
    :param input_dir: Input directory containing exported prompts.
    :param delete_prompt: Delete existing prompt before importing.
    :param use_threads: Use multithreading for import.
    :param mlflow_client: MLflow client.
    :return: Summary of import results.
    """
    
    if not has_prompt_support():
        _logger.warning(f"Prompt registry not supported in MLflow {mlflow.__version__} (requires 2.21.0+)")
        return {"unsupported": True, "mlflow_version": mlflow.__version__}
    
    mlflow_client = mlflow_client or create_mlflow_client()
    log_version_info()
    
    try:
        # Find all prompt directories to import
        prompt_dirs = _find_prompt_directories(input_dir)
        
        _logger.info(f"Found {len(prompt_dirs)} prompts to import")
        
        # Import prompts
        if use_threads:
            results = _import_prompts_threaded(prompt_dirs, mlflow_client, delete_prompt)
        else:
            results = _import_prompts_sequential(prompt_dirs, mlflow_client, delete_prompt)
        
        # Summary - categorize results
        successful = []
        skipped = []
        failed = []
        
        for result in results:
            if result is None:
                failed.append(result)
            elif isinstance(result, tuple) and len(result) == 2:
                name, version = result
                if version is None:
                    skipped.append(name)
                else:
                    successful.append(name)
            else:
                successful.append(result)
        
        summary = {
            "total_prompts": len(prompt_dirs),
            "successful_imports": len(successful),
            "skipped_imports": len(skipped),
            "failed_imports": len(failed)
        }
        
        if skipped:
            _logger.info(f"Skipped {len(skipped)} existing prompts: {', '.join(skipped)}")
        
        # Write summary
        summary_path = os.path.join(input_dir, "import_summary.json")
        io_utils.write_export_file(input_dir, "import_summary.json", __file__, summary)
        
        _logger.info(f"Prompt import completed: {summary}")
        return summary
        
    except Exception as e:
        _logger.error(f"Bulk prompt import failed: {str(e)}")
        return {"error": str(e)}


def _find_prompt_directories(input_dir):
    """Find all prompt directories in the input directory."""
    prompt_dirs = []
    
    if not os.path.exists(input_dir):
        raise Exception(f"Input directory does not exist: {input_dir}")
    
    # Look for directories that contain prompt.json files
    # Sort to ensure consistent ordering (important for version preservation)
    for item in sorted(os.listdir(input_dir)):
        item_path = os.path.join(input_dir, item)
        if os.path.isdir(item_path):
            prompt_file = os.path.join(item_path, "prompt.json")
            if os.path.exists(prompt_file):
                prompt_dirs.append({
                    "name": item,
                    "path": item_path
                })
                _logger.info(f"Found prompt directory: {item}")
            else:
                _logger.debug(f"Skipping directory '{item}': no prompt.json found")
    
    return prompt_dirs


def _import_prompts_sequential(prompt_dirs, mlflow_client, delete_prompt):
    """Import prompts sequentially."""
    results = []
    for prompt_dir in prompt_dirs:
        _logger.info(f"Importing prompt from: {prompt_dir['name']}")
        result = import_prompt(
            input_dir=prompt_dir["path"],
            prompt_name=None,  # Use original name from export
            delete_prompt=delete_prompt,
            mlflow_client=mlflow_client
        )
        results.append(result)
    return results


def _import_prompts_threaded(prompt_dirs, mlflow_client, delete_prompt):
    """Import prompts using multithreading."""
    def import_single(prompt_dir):
        _logger.info(f"Importing prompt from: {prompt_dir['name']}")
        return import_prompt(
            input_dir=prompt_dir["path"],
            prompt_name=None,  # Use original name from export
            delete_prompt=delete_prompt,
            mlflow_client=mlflow_client
        )
    
    max_workers = utils.get_threads(use_threads=True)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(import_single, prompt_dirs))
    
    return results


@click.command()
@opt_input_dir
@click.option("--delete-prompt",
    help="Delete existing prompt before importing.",
    type=bool,
    default=False
)
@click.option("--use-threads",
    help="Use multithreading for import.",
    is_flag=True,
    default=False
)
def main(input_dir, delete_prompt, use_threads):
    _logger.info("Options:")
    for k, v in locals().items():
        _logger.info(f"  {k}: {v}")
    
    result = import_prompts(
        input_dir=input_dir,
        delete_prompt=delete_prompt,
        use_threads=use_threads
    )
    
    # Check for failures
    if result is None:
        _logger.error("Prompt import failed with unknown error")
        sys.exit(1)
    elif "unsupported" in result:
        _logger.error(f"Prompt registry not supported in MLflow {result.get('mlflow_version')} (requires 2.21.0+)")
        sys.exit(1)
    elif "error" in result:
        _logger.error(f"Prompt import failed: {result['error']}")
        sys.exit(1)


if __name__ == "__main__":
    main()