"""
Imports multiple MLflow prompts from a directory.

Note: This implementation uses standard MLflow APIs (mlflow.genai.*) with fallbacks 
for different MLflow versions to ensure compatibility across various deployments.
"""

import os
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
        use_threads=False,
        mlflow_client=None
    ):
    """
    Import multiple prompts from a directory.
    
    :param input_dir: Input directory containing exported prompts.
    :param use_threads: Use multithreading for import.
    :param mlflow_client: MLflow client.
    :return: Summary of import results.
    """
    
    if not has_prompt_support():
        raise Exception(f"Prompt registry not supported in MLflow {mlflow.__version__} (requires 2.21.0+)")
    
    mlflow_client = mlflow_client or create_mlflow_client()
    log_version_info()
    
    try:
        # Find all prompt directories to import
        prompt_dirs = _find_prompt_directories(input_dir)
        
        _logger.info(f"Found {len(prompt_dirs)} prompts to import")
        
        # Import prompts
        if use_threads:
            results = _import_prompts_threaded(prompt_dirs)
        else:
            results = _import_prompts_sequential(prompt_dirs)
        
        # Summary
        successful = [r for r in results if r is not None]
        failed = len(results) - len(successful)
        
        summary = {
            "total_prompts": len(prompt_dirs),
            "successful_imports": len(successful),
            "failed_imports": failed
        }
        
        # Write summary
        summary_path = os.path.join(input_dir, "import_summary.json")
        io_utils.write_export_file(input_dir, "import_summary.json", __file__, summary)
        
        _logger.info(f"Prompt import completed: {summary}")
        return summary
        
    except Exception as e:
        _logger.error(f"Bulk prompt import failed: {str(e)}")
        return None


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
    
    return prompt_dirs


def _import_prompts_sequential(prompt_dirs):
    """Import prompts sequentially."""
    results = []
    for prompt_dir in prompt_dirs:
        _logger.info(f"Importing prompt from: {prompt_dir['name']}")
        result = import_prompt(
            input_dir=prompt_dir["path"],
            prompt_name=None  # Use original name from export
        )
        results.append(result)
    return results


def _import_prompts_threaded(prompt_dirs):
    """Import prompts using multithreading."""
    def import_single(prompt_dir):
        _logger.info(f"Importing prompt from: {prompt_dir['name']}")
        return import_prompt(
            input_dir=prompt_dir["path"],
            prompt_name=None  # Use original name from export
        )
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(import_single, prompt_dirs))
    
    return results


@click.command()
@opt_input_dir
@click.option("--use-threads",
    help="Use multithreading for import.",
    is_flag=True,
    default=False
)
def main(input_dir, use_threads):
    _logger.info("Options:")
    for k, v in locals().items():
        _logger.info(f"  {k}: {v}")
    
    import_prompts(
        input_dir=input_dir,
        use_threads=use_threads
    )


if __name__ == "__main__":
    main()