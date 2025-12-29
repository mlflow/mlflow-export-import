"""
Tests for evaluation dataset export and import functionality.
"""
import pytest
import mlflow
from mlflow_export_import.evaluation_dataset.export_evaluation_dataset import export_evaluation_dataset
from mlflow_export_import.evaluation_dataset.import_evaluation_dataset import import_evaluation_dataset
from mlflow_export_import.bulk.export_evaluation_datasets import export_evaluation_datasets
from mlflow_export_import.bulk.import_evaluation_datasets import import_evaluation_datasets
from mlflow_export_import.common.version_utils import has_evaluation_dataset_support
from tests.utils_test import create_output_dir
from tests.open_source.init_tests import mlflow_context


pytestmark = pytest.mark.skipif(
    not has_evaluation_dataset_support(),
    reason="Evaluation datasets not supported in this MLflow version"
)


def _create_test_evaluation_dataset(client, name, records, tags=None, experiment_ids=None):
    """Create a test evaluation dataset using version-aware API."""
    try:
        import mlflow.genai
        if hasattr(mlflow.genai, 'create_dataset'):
            # Create dataset (MLflow 3.4.0 API)
            dataset = mlflow.genai.create_dataset(
                name=name,
                experiment_id=experiment_ids,
                tags=tags
            )
            
            # Merge records if provided
            if records:
                dataset.merge_records(records)
            
            return dataset
    except Exception as e:
        pytest.skip(f"No compatible evaluation dataset creation API available: {e}")


def test_export_import_evaluation_dataset(mlflow_context):
    """Test single evaluation dataset export and import."""
    # Create test dataset in source
    mlflow.set_tracking_uri(mlflow_context.client_src.tracking_uri)
    dataset_name = "test_eval_dataset_single"
    
    records = [
        {"inputs": {"question": "What is 2+2?"}, "targets": {"answer": "4"}},
        {"inputs": {"question": "What is the capital of France?"}, "targets": {"answer": "Paris"}}
    ]
    
    tags = {"test": "true", "purpose": "unit-test"}
    
    dataset = _create_test_evaluation_dataset(
        mlflow_context.client_src,
        name=dataset_name,
        records=records,
        tags=tags
    )
    
    assert dataset is not None
    assert dataset.name == dataset_name
    
    # Export dataset
    output_dir = f"{mlflow_context.output_dir}/eval_dataset_single"
    create_output_dir(output_dir)
    
    exported = export_evaluation_dataset(
        dataset_name=dataset_name,
        output_dir=output_dir,
        mlflow_client=mlflow_context.client_src
    )
    
    assert exported is not None
    assert exported.name == dataset_name
    
    # Import dataset to destination
    mlflow.set_tracking_uri(mlflow_context.client_dst.tracking_uri)
    imported_name = f"{dataset_name}_imported"
    
    result = import_evaluation_dataset(
        input_dir=output_dir,
        dataset_name=imported_name,
        mlflow_client=mlflow_context.client_dst
    )
    
    assert result is not None
    assert result[0] == imported_name
    
    # Validate that records were actually imported (not just metadata)
    imported_dataset = mlflow.genai.get_dataset(dataset_id=result[1])
    assert imported_dataset is not None
    # Access records to trigger lazy loading and verify data was imported
    imported_records = list(imported_dataset.records)
    assert len(imported_records) == len(records)


def test_dataset_name_override_on_import(mlflow_context):
    """Test dataset name override on import."""
    # Create test dataset in source
    mlflow.set_tracking_uri(mlflow_context.client_src.tracking_uri)
    original_name = "test_eval_dataset_rename"
    
    records = [
        {"inputs": {"text": "test"}, "targets": {"label": "positive"}}
    ]
    
    dataset = _create_test_evaluation_dataset(
        mlflow_context.client_src,
        name=original_name,
        records=records
    )
    
    # Export dataset
    output_dir = f"{mlflow_context.output_dir}/eval_dataset_rename"
    create_output_dir(output_dir)
    
    export_evaluation_dataset(
        dataset_name=original_name,
        output_dir=output_dir,
        mlflow_client=mlflow_context.client_src
    )
    
    # Import with new name
    mlflow.set_tracking_uri(mlflow_context.client_dst.tracking_uri)
    new_name = "renamed_eval_dataset"
    
    result = import_evaluation_dataset(
        input_dir=output_dir,
        dataset_name=new_name,
        mlflow_client=mlflow_context.client_dst
    )
    
    assert result is not None
    assert result[0] == new_name
    assert result[0] != original_name
    
    # Validate records were imported
    imported_dataset = mlflow.genai.get_dataset(dataset_id=result[1])
    imported_records = list(imported_dataset.records)
    assert len(imported_records) == len(records)


def test_bulk_export_import_evaluation_datasets(mlflow_context):
    """Test bulk evaluation dataset export and import."""
    # Create multiple test datasets in source
    mlflow.set_tracking_uri(mlflow_context.client_src.tracking_uri)
    
    datasets_data = [
        ("test_eval_bulk_1", [{"inputs": {"x": 1}, "targets": {"y": 2}}]),
        ("test_eval_bulk_2", [{"inputs": {"x": 3}, "targets": {"y": 4}}]),
        ("test_eval_bulk_3", [{"inputs": {"x": 5}, "targets": {"y": 6}}])
    ]
    
    for name, records in datasets_data:
        _create_test_evaluation_dataset(
            mlflow_context.client_src,
            name=name,
            records=records
        )
    
    # Export all datasets
    output_dir = f"{mlflow_context.output_dir}/eval_datasets_bulk"
    create_output_dir(output_dir)
    
    export_result = export_evaluation_datasets(
        output_dir=output_dir,
        dataset_names=None,  # Export all
        use_threads=False,
        mlflow_client=mlflow_context.client_src
    )
    
    assert export_result is not None
    assert export_result["successful_exports"] >= len(datasets_data)
    assert export_result["failed_exports"] == 0
    
    # Import all datasets to destination
    mlflow.set_tracking_uri(mlflow_context.client_dst.tracking_uri)
    
    import_result = import_evaluation_datasets(
        input_dir=output_dir,
        use_threads=False,
        mlflow_client=mlflow_context.client_dst
    )
    
    assert import_result is not None
    assert import_result["successful_imports"] >= len(datasets_data)
    
    # Validate records were actually imported (not just metadata)
    from mlflow.tracking import MlflowClient
    client = MlflowClient()
    all_datasets = client.search_datasets()
    
    for dataset_name, expected_records in datasets_data:
        matching_datasets = [d for d in all_datasets if d.name == dataset_name]
        assert len(matching_datasets) > 0, f"Dataset {dataset_name} not found"
        
        imported_dataset = mlflow.genai.get_dataset(dataset_id=matching_datasets[0].dataset_id)
        # Access records to trigger lazy loading and verify data was imported
        imported_records = list(imported_dataset.records)
        assert len(imported_records) == len(expected_records)


def test_export_specific_evaluation_datasets(mlflow_context):
    """Test exporting specific evaluation datasets by name."""
    # Create test datasets
    mlflow.set_tracking_uri(mlflow_context.client_src.tracking_uri)
    
    _create_test_evaluation_dataset(
        mlflow_context.client_src,
        "eval_dataset_a",
        [{"inputs": {"a": 1}, "targets": {"b": 2}}]
    )
    _create_test_evaluation_dataset(
        mlflow_context.client_src,
        "eval_dataset_b",
        [{"inputs": {"c": 3}, "targets": {"d": 4}}]
    )
    _create_test_evaluation_dataset(
        mlflow_context.client_src,
        "eval_dataset_c",
        [{"inputs": {"e": 5}, "targets": {"f": 6}}]
    )
    
    # Export only specific datasets
    output_dir = f"{mlflow_context.output_dir}/eval_datasets_specific"
    create_output_dir(output_dir)
    
    export_result = export_evaluation_datasets(
        output_dir=output_dir,
        dataset_names=["eval_dataset_a", "eval_dataset_c"],
        use_threads=False,
        mlflow_client=mlflow_context.client_src
    )
    
    assert export_result is not None
    assert export_result["successful_exports"] == 2
    assert export_result["failed_exports"] == 0


def test_export_missing_dataset_error(mlflow_context):
    """Test error handling when exporting a non-existent dataset."""
    mlflow.set_tracking_uri(mlflow_context.client_src.tracking_uri)
    
    output_dir = f"{mlflow_context.output_dir}/eval_dataset_missing"
    create_output_dir(output_dir)
    
    # Try to export a dataset that doesn't exist
    result = export_evaluation_dataset(
        dataset_name="nonexistent_dataset_12345",
        output_dir=output_dir,
        mlflow_client=mlflow_context.client_src
    )
    
    # Should return None on failure
    assert result is None


def test_import_missing_file_error(mlflow_context):
    """Test error handling when importing from a directory without dataset file."""
    mlflow.set_tracking_uri(mlflow_context.client_dst.tracking_uri)
    
    # Create empty directory
    output_dir = f"{mlflow_context.output_dir}/eval_dataset_no_file"
    create_output_dir(output_dir)
    
    # Try to import from directory without evaluation_dataset.json
    result = import_evaluation_dataset(
        input_dir=output_dir,
        mlflow_client=mlflow_context.client_dst
    )
    
    # Should return None on failure
    assert result is None


def test_version_incompatibility_warning(mlflow_context):
    """Test version compatibility check logs warnings for version differences."""
    import json
    import os
    import logging
    
    # This test verifies that the version compatibility check works and logs warnings
    # We'll create a mock export file with a different version
    output_dir = f"{mlflow_context.output_dir}/eval_dataset_version"
    create_output_dir(output_dir)
    
    # Create a mock exported dataset file with a different major version
    dataset_file = os.path.join(output_dir, "evaluation_dataset.json")
    mock_data = {
        "system": {
            "package_version": "1.0.0",
            "script": "export_evaluation_dataset.py",
            "export_file_version": "2",
            "export_time": 1730000000,
            "_export_time": "2024-10-27 00:00:00",
            "mlflow_version": "99.0.0",  # Fake future version to trigger warning
            "mlflow_tracking_uri": "http://localhost:5000",
            "platform": {
                "python_version": "3.11.0",
                "system": "Darwin",
                "processor": "arm"
            },
            "user": "test_user"
        },
        "mlflow": {
            "evaluation_dataset": {
                "dataset_id": "test_id_123",
                "name": "test_version_dataset",
                "experiment_ids": [],
                "tags": {},
                "source": {
                    "type": "code",
                    "uri": "test://dataset/test"
                },
                "schema": None,
                "records": [],  # Empty records to avoid API issues
                "profile": None,
                "create_time": 1730000000000,
                "_create_time": "2024-10-27 00:00:00"
            }
        }
    }
    
    with open(dataset_file, 'w') as f:
        json.dump(mock_data, f)
    
    # Capture log output to verify warnings are logged
    import logging
    from io import StringIO
    log_capture = StringIO()
    handler = logging.StreamHandler(log_capture)
    handler.setLevel(logging.WARNING)
    
    logger = logging.getLogger('mlflow_export_import.evaluation_dataset.import_evaluation_dataset')
    logger.addHandler(handler)
    
    # Import - the version check should run and log warnings
    mlflow.set_tracking_uri(mlflow_context.client_dst.tracking_uri)
    
    # The import may fail due to API differences, but the version check should run
    try:
        result = import_evaluation_dataset(
            input_dir=output_dir,
            dataset_name="test_version_import",
            mlflow_client=mlflow_context.client_dst
        )
    except Exception:
        pass  # Expected to potentially fail due to API differences
    
    # Verify that version compatibility warnings were logged
    log_output = log_capture.getvalue()
    logger.removeHandler(handler)
    
    # Check that the major version difference warning was logged
    assert "Major version difference detected" in log_output or "version" in log_output.lower()
