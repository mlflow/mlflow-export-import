"""
Imports a logged model from a directory
"""

import os
import click
import mlflow
from mlflow.entities import RunStatus

from mlflow_export_import.common import utils, mlflow_utils, io_utils
from mlflow_export_import.common import filesystem as _fs
from mlflow_export_import.common.click_options import (
    opt_input_dir,
    opt_experiment_name
)
from mlflow_export_import.common import MlflowExportImportException
from mlflow_export_import.client.client_utils import create_mlflow_client
from mlflow_export_import.logged_model.logged_model_utils import update_logged_model_mlmodel_data
from mlflow_export_import.logged_model.logged_model_importer import _import_inputs, _log_metrics
from mlflow_export_import.common.version_utils import has_logged_model_support
from mlflow_export_import.client.client_utils import create_mlflow_client, create_dbx_client

_logger = utils.getLogger(__name__)

def import_logged_model(
        input_dir,
        experiment_name,
        run_id = None,
        mlmodel_fix = True,
        model_type = None,
        step = None,
        mlflow_client = None
    ):
    """
    :param input_dir: Directory containing logged model.
    :param experiment_name: Name of the experiment to add Logged Model to.
    :param run_id: Run id to add Logged Model to.
    :param mlmodel_fix: Add correct run ID in destination MLmodel artifact.
                        Can be expensive for deeply nested artifacts.
    :param model_type: Type of logged model to a run. Possible values output or input.
    :param step: Step to add Logged Model to run.
    :param mlflow_client: MLflow client.
    """
    if not has_logged_model_support():
        _logger.warning(f"Logged models are not supported in this MLflow version {mlflow.__version__} (requires 3.0+).")
        return {"unsupported": True, "mlflow_version": mlflow.__version__}

    mlflow_client = mlflow_client or create_mlflow_client()

    _logger.info(f"Importing logged model from '{input_dir}'")

    dbx_client = create_dbx_client(mlflow_client)
    exp = mlflow_utils.set_experiment(mlflow_client, dbx_client, experiment_name)
    src_logged_model_path = os.path.join(input_dir, "logged_model.json")
    src_logged_model_dct = io_utils.read_file_mlflow(src_logged_model_path)
    logged_model = None

    try:
        # This tag gets automatically created during import-model(s)
        src_logged_model_dct["tags"].pop("mlflow.modelVersions", None)
        logged_model_inputs = {
            "experiment_id": exp.experiment_id,
            "name": src_logged_model_dct["name"],
            "tags": src_logged_model_dct["tags"],
            "params": src_logged_model_dct["params"],
            "model_type": src_logged_model_dct["model_type"],
        }

        if src_logged_model_dct["source_run_id"]:
            if not run_id:
                run_id = mlflow_client.create_run(exp.experiment_id).info.run_id
                _import_inputs(mlflow_client, src_logged_model_dct, run_id)

            logged_model_inputs["source_run_id"] = run_id

        logged_model = mlflow_client.create_logged_model(**logged_model_inputs)

        if run_id:
            _log_metrics(mlflow_client, run_id, src_logged_model_dct["metrics"], logged_model.model_id)
            from mlflow.entities import LoggedModelOutput
            if model_type == "input":
                mlflow_client.log_inputs(run_id=run_id,
                                         models=[LoggedModelOutput(logged_model.model_id, step= step if step else 0)])
            else:
                mlflow_client.log_outputs(run_id=run_id,
                                         models=[LoggedModelOutput(logged_model.model_id, step=step if step else 0)])

        path = _fs.mk_local_path(os.path.join(input_dir, "artifacts"))

        if os.path.exists(path):
            mlflow_client.log_model_artifacts(logged_model.model_id, path)
            if mlmodel_fix:
                update_logged_model_mlmodel_data(mlflow_client, logged_model, os.path.join(path, "MLmodel"))

        mlflow_client.finalize_logged_model(logged_model.model_id, src_logged_model_dct["status"])
        mlflow_client.set_terminated(run_id, RunStatus.to_string(RunStatus.FINISHED))
        _logger.info(f"Imported logged model {src_logged_model_dct['name']} into experiment {exp.name}")
    except Exception as e:
        from mlflow.entities import LoggedModelStatus
        mlflow_client.finalize_logged_model(logged_model.model_id, LoggedModelStatus.FAILED)
        mlflow_client.set_terminated(run_id, RunStatus.to_string(RunStatus.FAILED))
        import traceback
        traceback.print_exc()
        raise MlflowExportImportException(e, f"Importing logged-model {src_logged_model_dct['name']} of experiment '{exp.name}' failed")


@click.command()
@opt_input_dir
@opt_experiment_name
@click.option("--mlmodel-fix",
    help="Add correct run ID in destination MLmodel artifact. Can be expensive for deeply nested artifacts.",
    type=bool,
    default=True,
    show_default=True
)

def main(input_dir,
         experiment_name,
         mlmodel_fix
    ):
    _logger.info("Options:")
    for k, v in locals().items():
        _logger.info(f"  {k}: {v}")

    import_logged_model(
        input_dir = input_dir,
        experiment_name = experiment_name,
        mlmodel_fix = mlmodel_fix)


if __name__ == "__main__":
    main()
