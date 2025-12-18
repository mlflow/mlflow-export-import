"""
Imports multiple MLflow GenAI evaluation datasets from a directory.

Note: Evaluation datasets are first-class entities introduced in MLflow 3.4.0+.
They require a SQL-based tracking backend (SQLite, PostgreSQL, MySQL).
FileStore backend is not supported.
"""

import os
import click
import mlflow
from concurrent.futures import ThreadPoolExecutor

from mlflow_export_import.common import utils, io_utils
from mlflow_export_import.common.click_options import (
    opt_input_dir,
    opt_delete_evaluation_dataset,
    opt_use_threads
)
from mlflow_export_import.common.version_utils import has_evaluation_dataset_support, log_version_info
from mlflow_export_import.client.client_utils import create_mlflow_client
from mlflow_export_import.evaluation_dataset.import_evaluation_dataset import import_evaluation_dataset

_logger = utils.getLogger(__name__)


def import_evaluation_datasets(
        input_dir,
        delete_dataset=False,
        use_threads=False,
        mlflow_client=None
    ):
    """
    Import multiple evaluation datasets from a directory.
    
    :param input_dir: Input directory containing exported datasets.
    :param delete_dataset: Delete existing dataset before importing (if it exists).
    :param use_threads: Use multithreading for import.
    :param mlflow_client: MLflow client.
    :return: Summary of import results.
    """
    
    if not has_evaluation_dataset_support():
        _logger.warning(f"Evaluation datasets not supported in MLflow {mlflow.__version__} (requires 3.4.0+)")
        return {"unsupported": True, "mlflow_version": mlflow.__version__}
    
    mlflow_client = mlflow_client or create_mlflow_client()
    log_version_info()
    
    try:
        # Find all dataset directories to import
        dataset_dirs = _find_dataset_directories(input_dir)
        
        _logger.info(f"Found {len(dataset_dirs)} datasets to import")
        
        # Import datasets
        results = _import_datasets(dataset_dirs, delete_dataset, use_threads)
        
        # Summary - categorize results
        successful = []
        skipped = []
        failed = []
        
        for result in results:
            if result is None:
                failed.append(result)
            elif isinstance(result, tuple) and len(result) == 2:
                name, dataset_id = result
                if dataset_id is None:
                    skipped.append(name)
                else:
                    successful.append(name)
            else:
                successful.append(result)
        
        summary = {
            "total_datasets": len(dataset_dirs),
            "successful_imports": len(successful),
            "skipped_imports": len(skipped),
            "failed_imports": len(failed)
        }
        
        if skipped:
            _logger.info(f"Skipped {len(skipped)} existing datasets: {', '.join(skipped)}")
        
        # Write summary
        io_utils.write_export_file(input_dir, "import_summary.json", __file__, summary)
        
        _logger.info(f"Evaluation dataset import completed: {summary}")
        return summary
        
    except Exception as e:
        _logger.error(f"Bulk evaluation dataset import failed: {str(e)}")
        return {"error": str(e)}


def _find_dataset_directories(input_dir):
    """Find all dataset directories containing evaluation_dataset.json."""
    dataset_dirs = []
    
    if not os.path.exists(input_dir):
        raise Exception(f"Input directory does not exist: {input_dir}")
    
    # Look for directories that contain evaluation_dataset.json files
    for item in os.listdir(input_dir):
        item_path = os.path.join(input_dir, item)
        if os.path.isdir(item_path):
            dataset_file = os.path.join(item_path, "evaluation_dataset.json")
            if os.path.exists(dataset_file):
                dataset_dirs.append({
                    "name": item,
                    "path": item_path
                })
                _logger.info(f"Found dataset directory: {item}")
    
    return dataset_dirs


def _import_datasets(dataset_dirs, delete_dataset, use_threads):
    """Import datasets with optional multithreading."""
    def import_single(dataset_dir):
        _logger.info(f"Importing dataset from: {dataset_dir['name']}")
        return import_evaluation_dataset(
            input_dir=dataset_dir["path"],
            dataset_name=None,  # Use original name from export
            delete_dataset=delete_dataset
        )
    
    max_workers = utils.get_threads(use_threads)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(import_single, dataset_dirs))
    
    return results


@click.command()
@opt_input_dir
@opt_delete_evaluation_dataset
@opt_use_threads
def main(input_dir, delete_evaluation_dataset, use_threads):
    _logger.info("Options:")
    for k, v in locals().items():
        _logger.info(f"  {k}: {v}")
    
    import_evaluation_datasets(
        input_dir=input_dir,
        delete_dataset=delete_evaluation_dataset,
        use_threads=use_threads
    )


if __name__ == "__main__":
    main()
