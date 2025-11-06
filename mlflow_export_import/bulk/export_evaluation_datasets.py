"""
Exports multiple MLflow GenAI evaluation datasets to a directory.

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
    opt_output_dir,
    opt_evaluation_datasets,
    opt_evaluation_datasets_experiment_ids,
    opt_use_threads
)
from mlflow_export_import.common.version_utils import has_evaluation_dataset_support, log_version_info
from mlflow_export_import.client.client_utils import create_mlflow_client
from mlflow_export_import.evaluation_dataset.export_evaluation_dataset import export_evaluation_dataset

_logger = utils.getLogger(__name__)


def export_evaluation_datasets(
        output_dir,
        dataset_names=None,
        experiment_ids=None,
        use_threads=False,
        mlflow_client=None
    ):
    """
    Export multiple evaluation datasets to a directory.
    
    :param output_dir: Output directory.
    :param dataset_names: List of dataset names to export. If None, exports all datasets.
    :param experiment_ids: List of experiment IDs to filter datasets. Only used when dataset_names is None.
    :param use_threads: Use multithreading for export.
    :param mlflow_client: MLflow client.
    :return: Summary of export results.
    """
    
    if not has_evaluation_dataset_support():
        _logger.warning(f"Evaluation datasets not supported in MLflow {mlflow.__version__} (requires 3.4.0+)")
        return {"unsupported": True, "mlflow_version": mlflow.__version__}
    
    mlflow_client = mlflow_client or create_mlflow_client()
    log_version_info()
    
    try:
        # Get list of datasets to export
        if dataset_names:
            datasets_to_export = _get_specified_datasets(dataset_names)
        else:
            datasets_to_export = _get_all_datasets(experiment_ids)
        
        _logger.info(f"Found {len(datasets_to_export)} datasets to export")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Export datasets
        results = _export_datasets(datasets_to_export, output_dir, use_threads)
        
        # Summary
        successful = [r for r in results if r is not None]
        failed = len(results) - len(successful)
        
        # Create dataset info list for summary
        dataset_info = []
        for dataset in datasets_to_export:
            dataset_info.append({
                "name": dataset.name,
                "dataset_id": dataset.dataset_id
            })
        
        summary = {
            "total_datasets": len(datasets_to_export),
            "successful_exports": len(successful),
            "failed_exports": failed,
            "datasets": dataset_info
        }
        
        # Write summary
        io_utils.write_export_file(output_dir, "evaluation_datasets_summary.json", __file__, summary)
        
        _logger.info(f"Evaluation dataset export completed: {summary}")
        return summary
        
    except Exception as e:
        _logger.error(f"Bulk evaluation dataset export failed: {str(e)}")
        return {"error": str(e)}


def _get_all_datasets(experiment_ids=None):
    """Get all available datasets from the registry using standard MLflow APIs."""
    
    # Try MLflow 3.4+ genai namespace
    try:
        import mlflow.genai
        if hasattr(mlflow.genai, 'search_datasets'):
            _logger.debug("Using mlflow.genai.search_datasets API")
            # Convert experiment_ids to list if provided
            exp_ids = experiment_ids if experiment_ids else None
            datasets = mlflow.genai.search_datasets(experiment_ids=exp_ids)
            return list(datasets)
    except (ImportError, AttributeError) as e:
        _logger.debug(f"mlflow.genai.search_datasets not available: {e}")
    except Exception as e:
        _logger.error(f"mlflow.genai.search_datasets failed: {e}")
        raise
    
    raise Exception(
        f"No compatible evaluation dataset search API found in MLflow {mlflow.__version__}. "
        f"Ensure MLflow 3.4.0+ is installed."
    )


def _get_specified_datasets(dataset_names):
    """Get specified datasets by name."""
    from mlflow.tracking import get_tracking_uri
    from mlflow.utils.uri import is_databricks_uri
    
    datasets = []
    
    # In Databricks, we can get by name directly
    # In non-Databricks, we need to search first to get dataset_id
    if is_databricks_uri(get_tracking_uri()):
        # Databricks: can use name directly
        from mlflow_export_import.evaluation_dataset.export_evaluation_dataset import _get_dataset_safe
        for dataset_name in dataset_names:
            try:
                dataset = _get_dataset_safe(name=dataset_name, dataset_id=None)
                if dataset:
                    datasets.append(dataset)
                else:
                    _logger.warning(f"Dataset '{dataset_name}' not found")
            except Exception as e:
                _logger.error(f"Error getting dataset '{dataset_name}': {e}")
    else:
        # Non-Databricks: search all datasets and filter by name
        all_datasets = _get_all_datasets()
        dataset_map = {d.name: d for d in all_datasets}
        
        for dataset_name in dataset_names:
            if dataset_name in dataset_map:
                datasets.append(dataset_map[dataset_name])
            else:
                _logger.warning(f"Dataset '{dataset_name}' not found")
    
    return datasets


def _export_datasets(datasets, output_dir, use_threads):
    """Export datasets with optional multithreading."""
    def export_single(dataset):
        dataset_dir = os.path.join(output_dir, f"{dataset.name}_{dataset.dataset_id}")
        return export_evaluation_dataset(
            dataset_name=dataset.name,
            dataset_id=dataset.dataset_id,
            output_dir=dataset_dir
        )
    
    max_workers = utils.get_threads(use_threads)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(export_single, datasets))
    
    return results


@click.command()
@opt_output_dir
@opt_evaluation_datasets
@opt_evaluation_datasets_experiment_ids
@opt_use_threads
def main(output_dir, evaluation_datasets, experiment_ids, use_threads):
    _logger.info("Options:")
    for k, v in locals().items():
        _logger.info(f"  {k}: {v}")
    
    # Handle 'all', file, or comma-separated list
    if evaluation_datasets.endswith(".txt"):
        with open(evaluation_datasets, 'r') as f:
            dataset_names_list = [line.strip() for line in f if line.strip()]
    elif evaluation_datasets.lower() == 'all':
        dataset_names_list = None  # Export all
    else:
        dataset_names_list = [name.strip() for name in evaluation_datasets.split(",")]
    
    experiment_ids_list = None
    if experiment_ids:
        experiment_ids_list = [exp_id.strip() for exp_id in experiment_ids.split(",")]
    
    export_evaluation_datasets(
        output_dir=output_dir,
        dataset_names=dataset_names_list,
        experiment_ids=experiment_ids_list,
        use_threads=use_threads
    )


if __name__ == "__main__":
    main()
