"""
Imports MLflow GenAI evaluation datasets from a directory.

Note: Evaluation datasets are first-class entities introduced in MLflow 3.4.0+.
They require a SQL-based tracking backend (SQLite, PostgreSQL, MySQL).
FileStore backend is not supported.
"""

import os
import json
import click
import mlflow
from packaging import version
from mlflow.exceptions import RestException
from mlflow.tracking import get_tracking_uri
from mlflow.utils.uri import is_databricks_uri

from mlflow_export_import.common import utils, io_utils
from mlflow_export_import.common.click_options import opt_input_dir
from mlflow_export_import.common.version_utils import has_evaluation_dataset_support, log_version_info, get_mlflow_version, get_version_info
from mlflow_export_import.client.client_utils import create_mlflow_client

_logger = utils.getLogger(__name__)


def _check_import_compatibility(dataset_data):
    """Check compatibility between source (exported) and target (current) MLflow versions."""
    # Get source version info from exported data
    system_info = dataset_data.get("system", {})
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
        
        # Check if target supports evaluation datasets
        if not target_info["supports_evaluation_datasets"]:
            raise Exception(
                f"Target MLflow {target_version} does not support evaluation datasets (requires 3.4.0+)"
            )
        
        # Warn about major version differences
        if source_ver.major != target_ver.major:
            _logger.warning(
                f"Major version difference detected: source v{source_ver.major} → target v{target_ver.major}"
            )
            _logger.warning("Some features may not be fully compatible")
        
        _logger.info("Version compatibility check passed")
        
    except Exception as e:
        _logger.warning(f"Could not parse version information: {e}")
        _logger.info("Proceeding with import (version check inconclusive)")


def import_evaluation_dataset(
        input_dir,
        dataset_name=None,
        delete_dataset=False,
        mlflow_client=None
    ):
    """
    Import an evaluation dataset from exported directory.
    
    :param input_dir: Input directory containing exported dataset.
    :param dataset_name: Optional new name for the imported dataset. If None, uses original name.
    :param delete_dataset: Delete existing dataset before importing (if it exists).
    :param mlflow_client: MLflow client (not used for genai API but kept for consistency).
    :return: Tuple of (name, dataset_id) or None if import failed.
    """
    
    if not has_evaluation_dataset_support():
        raise Exception(
            f"Evaluation datasets not supported in MLflow {mlflow.__version__} (requires 3.4.0+)"
        )
    
    mlflow_client = mlflow_client or create_mlflow_client()
    log_version_info()
    
    try:
        # Read exported dataset data
        dataset_path = os.path.join(input_dir, "evaluation_dataset.json")
        if not os.path.exists(dataset_path):
            raise Exception(f"Evaluation dataset export file not found: {dataset_path}")
        
        # Read full export file for version compatibility check
        with open(dataset_path, 'r') as f:
            full_export_data = json.load(f)
        
        # Check version compatibility between source and target
        _check_import_compatibility(full_export_data)
        
        # Read MLflow-specific data for import
        dataset_data = io_utils.read_file_mlflow(dataset_path)
        
        _logger.info(f"Importing evaluation dataset from: {input_dir}")
        
        # Extract dataset information
        dataset_info = dataset_data.get("evaluation_dataset", {})
        
        # Use provided name or original name
        final_dataset_name = dataset_name or dataset_info.get("name")
        if not final_dataset_name:
            raise Exception("No dataset name specified and none found in export data")
        
        # Check if dataset already exists
        existing_dataset = None
        try:
            import mlflow.genai
            datasets = list(mlflow.genai.search_datasets())
            matching = [d for d in datasets if d.name == final_dataset_name]
            if matching:
                existing_dataset = matching[0]
                _logger.info(f"Found existing dataset: {final_dataset_name} (ID: {existing_dataset.dataset_id})")
        except Exception as e:
            _logger.debug(f"Could not search for existing dataset: {e}")
        
        # Delete existing dataset if requested
        if delete_dataset and existing_dataset:
            try:
                _delete_dataset_safe(dataset_id=existing_dataset.dataset_id)
                _logger.info(f"Deleted existing dataset: {final_dataset_name}")
                existing_dataset = None
            except Exception as e:
                _logger.warning(f"Could not delete dataset '{final_dataset_name}': {e}")
        
        # Skip import if dataset already exists and delete not requested
        if existing_dataset and not delete_dataset:
            _logger.warning(
                f"Evaluation dataset '{final_dataset_name}' already exists - skipping import. "
                f"Use --delete-evaluation-dataset to replace."
            )
            return (final_dataset_name, existing_dataset.dataset_id)
        
        # Extract dataset components
        source = dataset_info.get("source", {})
        schema = dataset_info.get("schema")
        records = dataset_info.get("records", [])
        tags = dataset_info.get("tags", {})
        experiment_ids = dataset_info.get("experiment_ids", [])
        
        # Create dataset in destination
        try:
            imported_dataset = _create_dataset_safe(
                name=final_dataset_name,
                source=source,  # Not used in MLflow 3.4.0 but kept for future compatibility
                schema=schema,  # Not used in MLflow 3.4.0 but kept for future compatibility
                experiment_ids=experiment_ids,
                tags=tags
            )
        except Exception as e:
            error_msg = str(e)
            # Check if it's a duplicate name error - this is a fallback in case search didn't catch it
            if "already exists" in error_msg.lower() or "duplicate" in error_msg.lower() or "RESOURCE_ALREADY_EXISTS" in error_msg:
                _logger.warning(
                    f"Evaluation dataset '{final_dataset_name}' already exists - skipping import. "
                    f"Use --delete-evaluation-dataset to replace."
                )
                return (final_dataset_name, None)
            else:
                # Re-raise if it's not a duplicate error
                raise
        
        # Merge records if dataset has records
        if records:
            _logger.info(f"Merging {len(records)} records into dataset")
            imported_dataset = _merge_records_safe(imported_dataset, records)
        
        dataset_id = imported_dataset.dataset_id if hasattr(imported_dataset, 'dataset_id') else None
        _logger.info(f"Successfully imported evaluation dataset: {final_dataset_name} (ID: {dataset_id})")
        
        return (final_dataset_name, dataset_id)
        
    except Exception as e:
        error_msg = str(e)
        # Check for FileStore backend error
        if "FileStore" in error_msg or "SQL-based tracking backend" in error_msg:
            _logger.error(
                f"Evaluation datasets require SQL backend (SQLite, PostgreSQL, MySQL). "
                f"FileStore is not supported. Error: {error_msg}"
            )
        else:
            _logger.error(f"Evaluation dataset import failed: {error_msg}")
        return None


def _create_dataset_safe(name, source, schema=None, experiment_ids=None, tags=None):
    """Create dataset with version-aware API calls - ensures compatibility across MLflow deployments."""
    
    # Try MLflow 3.4+ genai namespace
    try:
        import mlflow.genai
        if hasattr(mlflow.genai, 'create_dataset'):
            # MLflow 3.4.0 API only accepts: name, experiment_id, tags
            # source and schema are not parameters - they're set automatically or via records
            # IMPORTANT: Use [] to create truly independent datasets (no experiment association)
            # Using None would default to experiment "0" (Default experiment)
            return mlflow.genai.create_dataset(
                name=name,
                experiment_id=experiment_ids if experiment_ids is not None else [],
                tags=tags
            )
    except (ImportError, AttributeError) as e:
        _logger.debug(f"mlflow.genai.create_dataset not available: {e}")
    except Exception as e:
        _logger.debug(f"mlflow.genai.create_dataset failed for '{name}': {e}")
        raise
    
    raise Exception(
        f"No compatible evaluation dataset API found in MLflow {mlflow.__version__}. "
        f"Ensure MLflow 3.4.0+ is installed."
    )


def _merge_records_safe(dataset, records):
    """Merge records into dataset with version-aware API calls."""
    
    try:
        if hasattr(dataset, 'merge_records'):
            # merge_records returns a new dataset object
            return dataset.merge_records(records)
    except Exception as e:
        _logger.debug(f"dataset.merge_records failed: {e}")
        raise
    
    raise Exception(
        f"No compatible method to merge records found in MLflow {mlflow.__version__}"
    )


def _set_dataset_tags_safe(dataset, tags):
    """Set dataset tags with version-aware API calls."""
    
    # Try mlflow.genai.set_dataset_tags
    try:
        import mlflow.genai
        if hasattr(mlflow.genai, 'set_dataset_tags'):
            mlflow.genai.set_dataset_tags(
                dataset_id=dataset.dataset_id,
                tags=tags
            )
            return dataset
    except (ImportError, AttributeError) as e:
        _logger.debug(f"mlflow.genai.set_dataset_tags not available: {e}")
    except Exception as e:
        _logger.debug(f"mlflow.genai.set_dataset_tags failed: {e}")
        raise
    
    raise Exception(
        f"No compatible method to set dataset tags found in MLflow {mlflow.__version__}"
    )


def _delete_dataset_safe(name=None, dataset_id=None):
    """Delete dataset with version-aware API calls."""
    # Try mlflow.genai.delete_dataset
    try:
        import mlflow.genai
        if hasattr(mlflow.genai, 'delete_dataset'):
            # In Databricks: use name parameter
            # Outside Databricks: use dataset_id parameter
            if is_databricks_uri(get_tracking_uri()):
                mlflow.genai.delete_dataset(name=name)
            else:
                # For non-Databricks, we need to get the dataset_id first
                if not dataset_id:
                    # Search for the dataset by name to get its ID
                    datasets = mlflow.genai.search_datasets()
                    for ds in datasets:
                        if ds.name == name:
                            dataset_id = ds.dataset_id
                            break
                if dataset_id:
                    mlflow.genai.delete_dataset(dataset_id=dataset_id)
            return
    except (ImportError, AttributeError) as e:
        _logger.debug(f"mlflow.genai.delete_dataset not available: {e}")
    except Exception as e:
        _logger.debug(f"mlflow.genai.delete_dataset failed: {e}")
        raise
    
    raise Exception(
        f"No compatible method to delete dataset found in MLflow {mlflow.__version__}"
    )


@click.command()
@opt_input_dir
@click.option("--evaluation-dataset-name",
    help="Optional new name for the imported evaluation dataset. If not specified, uses original name.",
    type=str,
    required=False
)
@click.option("--delete-evaluation-dataset",
    help="Delete existing evaluation dataset before importing.",
    type=bool,
    default=False
)
def main(input_dir, evaluation_dataset_name, delete_evaluation_dataset):
    _logger.info("Options:")
    for k, v in locals().items():
        _logger.info(f"  {k}: {v}")
    
    import_evaluation_dataset(
        input_dir=input_dir,
        dataset_name=evaluation_dataset_name,
        delete_dataset=delete_evaluation_dataset
    )


if __name__ == "__main__":
    main()
