"""
Tests for prompt export and import functionality.
"""
import pytest
import mlflow
from mlflow_export_import.prompt.export_prompt import export_prompt
from mlflow_export_import.prompt.import_prompt import import_prompt
from mlflow_export_import.bulk.export_prompts import export_prompts
from mlflow_export_import.bulk.import_prompts import import_prompts
from mlflow_export_import.common.version_utils import has_prompt_support
from tests.utils_test import create_output_dir
from tests.open_source.init_tests import mlflow_context


pytestmark = pytest.mark.skipif(
    not has_prompt_support(),
    reason="Prompt registry not supported in this MLflow version"
)


def _create_test_prompt(client, name, template, tags=None):
    """Create a test prompt using version-aware API."""
    try:
        import mlflow.genai
        if hasattr(mlflow.genai, 'register_prompt'):
            return mlflow.genai.register_prompt(
                name=name,
                template=template,
                tags=tags or {}
            )
    except Exception:
        pass
    
    # Fallback to top-level API
    if hasattr(mlflow, 'register_prompt'):
        return mlflow.register_prompt(
            name=name,
            template=template,
            tags=tags or {}
        )
    
    pytest.skip("No compatible prompt creation API available")


def test_export_import_prompt(mlflow_context):
    """Test single prompt export and import."""
    # Create test prompt in source
    mlflow.set_tracking_uri(mlflow_context.client_src.tracking_uri)
    prompt_name = "test_prompt_single"
    template = "Hello {name}, welcome to {place}!"
    
    prompt = _create_test_prompt(
        mlflow_context.client_src,
        name=prompt_name,
        template=template,
        tags={"test": "true", "purpose": "unit-test"}
    )
    
    # Export prompt
    output_dir = f"{mlflow_context.output_dir}/prompt_single"
    create_output_dir(output_dir)
    
    exported = export_prompt(
        prompt_name=prompt_name,
        prompt_version=str(prompt.version),
        output_dir=output_dir,
        mlflow_client=mlflow_context.client_src
    )
    
    assert exported is not None
    assert exported.name == prompt_name
    
    # Import prompt to destination
    mlflow.set_tracking_uri(mlflow_context.client_dst.tracking_uri)
    imported_name = f"{prompt_name}_imported"
    
    result = import_prompt(
        input_dir=output_dir,
        prompt_name=imported_name,
        mlflow_client=mlflow_context.client_dst
    )
    
    assert result is not None
    assert result[0] == imported_name


def test_bulk_export_import_prompts(mlflow_context):
    """Test bulk prompt export and import."""
    # Create multiple test prompts in source
    mlflow.set_tracking_uri(mlflow_context.client_src.tracking_uri)
    
    prompts_data = [
        ("test_prompt_bulk_1", "Template 1: {var1}"),
        ("test_prompt_bulk_2", "Template 2: {var2}"),
        ("test_prompt_bulk_3", "Template 3: {var3}")
    ]
    
    for name, template in prompts_data:
        _create_test_prompt(
            mlflow_context.client_src,
            name=name,
            template=template
        )
    
    # Export all prompts
    output_dir = f"{mlflow_context.output_dir}/prompts_bulk"
    create_output_dir(output_dir)
    
    export_result = export_prompts(
        output_dir=output_dir,
        prompt_names=None,  # Export all
        use_threads=False,
        mlflow_client=mlflow_context.client_src
    )
    
    assert export_result is not None
    assert export_result["successful_exports"] >= len(prompts_data)
    assert export_result["failed_exports"] == 0
    
    # Import all prompts to destination
    mlflow.set_tracking_uri(mlflow_context.client_dst.tracking_uri)
    
    import_result = import_prompts(
        input_dir=output_dir,
        use_threads=False,
        mlflow_client=mlflow_context.client_dst
    )
    
    assert import_result is not None
    assert import_result["successful_imports"] >= len(prompts_data)


def test_export_specific_prompts(mlflow_context):
    """Test exporting specific prompts by name."""
    # Create test prompts
    mlflow.set_tracking_uri(mlflow_context.client_src.tracking_uri)
    
    _create_test_prompt(mlflow_context.client_src, "prompt_a", "Template A")
    _create_test_prompt(mlflow_context.client_src, "prompt_b", "Template B")
    _create_test_prompt(mlflow_context.client_src, "prompt_c", "Template C")
    
    # Export only specific prompts
    output_dir = f"{mlflow_context.output_dir}/prompts_specific"
    create_output_dir(output_dir)
    
    export_result = export_prompts(
        output_dir=output_dir,
        prompt_names=["prompt_a", "prompt_c"],
        use_threads=False,
        mlflow_client=mlflow_context.client_src
    )
    
    assert export_result is not None
    assert export_result["successful_exports"] == 2
    assert export_result["failed_exports"] == 0
