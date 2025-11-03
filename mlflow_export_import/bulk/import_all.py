"""
Imports all MLflow objects: models, experiments, runs, prompts, and evaluation datasets.
"""

import os
import json
import click

import mlflow
from mlflow_export_import.common.click_options import (
    opt_input_dir,
    opt_delete_model,
    opt_use_src_user_id,
    opt_verbose,
    opt_import_permissions,
    opt_import_source_tags,
    opt_experiment_rename_file,
    opt_model_rename_file,
    opt_use_threads
)
from mlflow_export_import.common import utils
from mlflow_export_import.client.client_utils import create_mlflow_client
from mlflow_export_import.bulk.import_models import import_models
from mlflow_export_import.bulk.import_prompts import import_prompts
from mlflow_export_import.bulk import rename_utils

_logger = utils.getLogger(__name__)


def import_all(
        input_dir,
        delete_model,
        delete_prompt = False,
        import_permissions = False,
        import_source_tags = False,
        use_src_user_id = False,
        experiment_renames = None,
        model_renames = None,
        verbose = False,
        use_threads = False,
        mlflow_client = None
    ):
    """
    Import all MLflow objects: models, experiments, runs, and prompts.
    This delegates to import_models() and then adds prompt import on top.
    """
    mlflow_client = mlflow_client or create_mlflow_client()
    
    # Import models and their backing experiments
    models_result = import_models(
        input_dir = input_dir,
        delete_model = delete_model,
        import_permissions = import_permissions,
        import_source_tags = import_source_tags,
        use_src_user_id = use_src_user_id,
        experiment_renames = experiment_renames,
        model_renames = model_renames,
        verbose = verbose,
        use_threads = use_threads,
        mlflow_client = mlflow_client
    )
    
    # Import prompts if they exist (returns dict with status)
    prompt_res = None
    prompts_dir = os.path.join(input_dir, "prompts")
    if os.path.exists(prompts_dir):
        try:
            _logger.info("Importing prompts...")
            prompt_res = import_prompts(
                input_dir = prompts_dir,
                delete_prompt = delete_prompt,
                use_threads = use_threads,
                mlflow_client = mlflow_client
            )
            # Log if unsupported but don't fail
            if prompt_res and "unsupported" in prompt_res:
                _logger.warning(f"Prompts not supported in MLflow {prompt_res.get('mlflow_version')}")
            elif prompt_res and "error" in prompt_res:
                _logger.warning(f"Failed to import prompts: {prompt_res['error']}")
        except Exception as e:
            _logger.warning(f"Failed to import prompts: {e}")
            prompt_res = {"error": str(e)}
    
    # Add prompts to the report
    models_result["prompts_import"] = prompt_res
    _logger.info("\nImport-all report:")
    _logger.info(f"{json.dumps(models_result, indent=2)}\n")


@click.command()
@opt_input_dir
@opt_delete_model
@click.option("--delete-prompt",
    help="Delete existing prompts before importing.",
    type=bool,
    default=False
)
@opt_import_permissions
@opt_experiment_rename_file
@opt_model_rename_file
@opt_import_source_tags
@opt_use_src_user_id
@opt_use_threads
@opt_verbose

def main(input_dir, delete_model, delete_prompt,
        import_permissions,
        experiment_rename_file,
        model_rename_file,
        import_source_tags,
        use_src_user_id,
        use_threads,
        verbose,
    ):
    _logger.info("Options:")
    for k,v in locals().items():
        _logger.info(f"  {k}: {v}")

    import_all(
        input_dir = input_dir,
        delete_model = delete_model,
        delete_prompt = delete_prompt,
        import_permissions = import_permissions,
        experiment_renames = rename_utils.get_renames(experiment_rename_file),
        model_renames = rename_utils.get_renames(model_rename_file),
        import_source_tags = import_source_tags,
        use_src_user_id = use_src_user_id,
        verbose = verbose,
        use_threads = use_threads
    )


if __name__ == "__main__":
    main()
