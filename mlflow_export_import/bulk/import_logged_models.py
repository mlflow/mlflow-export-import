"""
Import a list of logged models from a directory
"""

import os
import click
import mlflow

from mlflow_export_import.common.click_options import (
    opt_input_dir,
    opt_experiment_name
)
from mlflow_export_import.common import utils, io_utils
from mlflow_export_import.logged_model.import_logged_model import import_logged_model

_logger = utils.getLogger(__name__)

def import_logged_models(
        input_dir,
        mlflow_client = None
    ):
    """
    :param input_dir: Source Logged models directory
    :param mlflow_client: Mlflow client
    """
    mlflow_client = mlflow_client or mlflow.MlflowClient()
    dct = io_utils.read_file_mlflow(os.path.join(input_dir, "logged_models.json"))
    exps = dct["experiments"]
    _logger.info(f"Importing logged models")
    for exp in exps:
        _logger.info(f"Importing from experiment: {exp['name']}")
        _logger.info(f"  Importing logged models: {exp['logged_models']}")

    for exp in exps:
        _import_logged_models(
            exp_name = exp["name"],
            input_dir = input_dir,
            logged_models = exp["logged_models"],
            mlflow_client = mlflow_client
        )


def _import_logged_models(
        exp_name,
        input_dir,
        logged_models,
        mlflow_client
        ):
    try:
        for model_id in logged_models:
            import_logged_model(
                input_dir = os.path.join(input_dir, model_id),
                experiment_name = exp_name,
                mlflow_client = mlflow_client
            )
        return logged_models
    except Exception as e:
        msg = { "experiment": exp_name, "logged_models": logged_models, "Exception": str(e) }
        import traceback
        traceback.print_exc()
        _logger.error(f"Failed to import logged models: {msg}")
        return None

@click.command()
@opt_input_dir
def main(input_dir):
    _logger.info("Options:")
    for k, v in locals().items():
        _logger.info(f"  {k}: {v}")
    import_logged_models(input_dir = input_dir)


if __name__ == "__main__":
    main()