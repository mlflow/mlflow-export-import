"""
Imports a registered model version and its run.
"""

import os
import click

from mlflow_export_import.common.click_options import (
    opt_input_dir,
    opt_model,
    opt_import_source_tags
)
from . click_options import (
    opt_create_model,
    opt_experiment_name
)
from mlflow_export_import.common import utils, io_utils, model_utils
from mlflow_export_import.model.import_model import ModelImporter
from mlflow_export_import.run.import_run import import_run

_logger = utils.getLogger(__name__)


def import_model_version(
        model_name,
        experiment_name,
        input_dir,
        create_model = False,
        import_source_tags = False,
        mlflow_client = None
    ):
    path = os.path.join(input_dir, "model_version.json")
    vr = io_utils.read_file_mlflow(path)["model_version"]

    path = os.path.join(input_dir, "run")
    dst_run, _ = import_run(
        input_dir = path,
        experiment_name = experiment_name,
        import_source_tags = import_source_tags,
        mlflow_client = mlflow_client
    )
    if create_model:
        model_utils.create_model(mlflow_client, model_name)

    model_importer = ModelImporter(
        import_source_tags = import_source_tags,
        mlflow_client = mlflow_client
    )
    model_importer.import_version(
        model_name = model_name,
        src_vr = vr,
        dst_run_id = dst_run.info.run_id
    )


@click.command()
@opt_input_dir
@opt_model
@opt_create_model
@opt_experiment_name
@opt_import_source_tags

def main(input_dir, model, experiment_name, create_model, import_source_tags):
    """
    Imports a registered model version and its run.
    """
    _logger.info("Options:")
    for k,v in locals().items():
        _logger.info(f"  {k}: {v}")
    import_model_version(
        model_name = model,
        experiment_name = experiment_name,
        input_dir = input_dir,
        create_model = create_model,
        import_source_tags = import_source_tags
    )


if __name__ == "__main__":
    main()
