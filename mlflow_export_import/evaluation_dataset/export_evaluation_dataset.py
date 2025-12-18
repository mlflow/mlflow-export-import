"""
Exports MLflow GenAI evaluation datasets to a directory.

Note: Evaluation datasets are first-class entities introduced in MLflow 3.4.0+.
They require a SQL-based tracking backend (SQLite, PostgreSQL, MySQL).
FileStore backend is not supported.
"""

import os
import click
import mlflow
from mlflow.exceptions import RestException
from mlflow.tracking import get_tracking_uri
from mlflow.utils.uri import is_databricks_uri

from mlflow_export_import.common import utils, io_utils
from mlflow_export_import.common.click_options import opt_output_dir
from mlflow_export_import.common.timestamp_utils import adjust_timestamps
from mlflow_export_import.common.version_utils import has_evaluation_dataset_support, log_version_info
from mlflow_export_import.client.client_utils import create_mlflow_client

_logger = utils.getLogger(__name__)


def export_evaluation_dataset(
        output_dir,
        dataset_name=None,
        dataset_id=None,
        mlflow_client=None
    ):
    """
    Export a single evaluation dataset to a directory.
    
    :param output_dir: Output directory.
    :param dataset_name: Name of the dataset to export. Either dataset_name or dataset_id must be provided.
    :param dataset_id: ID of the dataset to export. Either dataset_name or dataset_id must be provided.
    :param mlflow_client: MLflow client (not used for genai API but kept for consistency).
    :return: Dataset object or None if export failed.
    :raises ValueError: If neither dataset_name nor dataset_id is provided.
    """
    
    if not has_evaluation_dataset_support():
        raise Exception(f"Evaluation datasets not supported in MLflow {mlflow.__version__} (requires 3.4.0+)")
    
    if not dataset_name and not dataset_id:
        raise ValueError("Either dataset_name or dataset_id must be provided")
    
    mlflow_client = mlflow_client or create_mlflow_client()
    log_version_info()
    
    try:
        # Get the dataset using mlflow.genai API
        dataset = _get_dataset_safe(name=dataset_name, dataset_id=dataset_id)
        
        identifier = dataset_name or dataset_id
        _logger.info(f"Exporting evaluation dataset: {identifier}")
        
        # Serialize dataset to dictionary
        dataset_dict = dataset.to_dict()
        
        # Adjust timestamps for readability
        if "create_time" in dataset_dict:
            adjust_timestamps(dataset_dict, ["create_time"])
        
        mlflow_attr = {
            "evaluation_dataset": dataset_dict
        }
        
        # Write dataset export file
        io_utils.write_export_file(output_dir, "evaluation_dataset.json", __file__, mlflow_attr)
        
        _logger.info(f"Successfully exported evaluation dataset: {identifier}")
        return dataset
        
    except RestException as e:
        _logger.error(f"Evaluation dataset export failed: {{'dataset_name': '{dataset_name}', 'dataset_id': '{dataset_id}', 'RestException': {e.json}}}")
        return None
    except Exception as e:
        error_msg = str(e)
        # Check for FileStore backend error
        if "FileStore" in error_msg or "SQL-based tracking backend" in error_msg:
            _logger.error(
                f"Evaluation datasets require SQL backend (SQLite, PostgreSQL, MySQL). "
                f"FileStore is not supported. Error: {error_msg}"
            )
        else:
            _logger.error(f"Evaluation dataset export failed: {{'dataset_name': '{dataset_name}', 'dataset_id': '{dataset_id}', 'Exception': {error_msg}}}")
        return None


def _get_dataset_safe(name=None, dataset_id=None):
    """Get dataset with version-aware API calls - ensures compatibility across MLflow deployments."""
    
    # Try MLflow 3.4+ genai namespace
    try:
        import mlflow.genai
        if hasattr(mlflow.genai, 'get_dataset'):
            # In Databricks: use name parameter only
            # Outside Databricks: use dataset_id parameter only
            if is_databricks_uri(get_tracking_uri()):
                return mlflow.genai.get_dataset(name=name)
            else:
                # If name provided but not dataset_id, search for it
                if name and not dataset_id:
                    _logger.info(f"Looking up dataset_id for name: {name}")
                    datasets = list(mlflow.genai.search_datasets())
                    matching = [d for d in datasets if d.name == name]
                    if not matching:
                        raise ValueError(f"Dataset with name '{name}' not found")
                    if len(matching) > 1:
                        _logger.warning(f"Multiple datasets found with name '{name}', using first match")
                    dataset_id = matching[0].dataset_id
                    _logger.info(f"Found dataset_id: {dataset_id}")
                
                if not dataset_id:
                    raise ValueError("Parameter 'dataset_id' is required. Use search_datasets() to find the dataset ID by name if needed.")
                
                return mlflow.genai.get_dataset(dataset_id=dataset_id)
    except (ImportError, AttributeError) as e:
        _logger.debug(f"mlflow.genai.get_dataset not available: {e}")
    except Exception as e:
        _logger.debug(f"mlflow.genai.get_dataset failed: {e}")
        raise
    
    raise Exception(
        f"No compatible evaluation dataset API found in MLflow {mlflow.__version__}. "
        f"Ensure MLflow 3.4.0+ is installed."
    )


@click.command()
@click.option("--dataset-name",
    help="Name of the evaluation dataset to export.",
    type=str,
    required=False
)
@click.option("--dataset-id",
    help="ID of the evaluation dataset to export.",
    type=str,
    required=False
)
@opt_output_dir
def main(dataset_name, dataset_id, output_dir):
    _logger.info("Options:")
    for k, v in locals().items():
        _logger.info(f"  {k}: {v}")
    
    export_evaluation_dataset(
        output_dir=output_dir,
        dataset_name=dataset_name,
        dataset_id=dataset_id
    )


if __name__ == "__main__":
    main()
