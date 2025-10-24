"""
Exports logged models to a directory.
"""

import os

import mlflow
import click
from mlflow.exceptions import RestException

from mlflow_export_import.common.click_options import (
    opt_experiment_ids,
    opt_output_dir
)
from mlflow_export_import.common import MlflowExportImportException
from mlflow_export_import.common import utils, io_utils, mlflow_utils
from mlflow_export_import.bulk.bulk_utils import get_logged_models, get_experiment_ids
from mlflow_export_import.logged_model.export_logged_model import export_logged_model

_logger = utils.getLogger(__name__)

def export_logged_models(
        experiment_ids,
        output_dir,
        logged_models_filter = None,
        mlflow_client = None
    ):
    """
    :param experiment_ids: can be either:
      - List of Experiment Ids
      - String with comma-delimited experiment IDs such as '1,2' or 'all'
    :param output_dir: Directory where logged models will be exported
    :param logged_models_filter: Filter logged models based on run ids to experiments.
    :param mlflow_client: Mlflow client
    """
    mlflow_client = mlflow_client or mlflow.MlflowClient()

    if isinstance(experiment_ids, str):
        experiment_ids = get_experiment_ids(mlflow_client, experiment_ids)

    ok_logged_models = []
    failed_logged_models = []
    nums_logged_models_exported = 0

    export_results = {
        exp_id: {
            "id": exp_id,
            "name": mlflow_client.get_experiment(exp_id).name,
            "logged_models": []} for exp_id in experiment_ids
    }

    logged_models = get_logged_models(mlflow_client, experiment_ids)

    if logged_models_filter:
        logged_models = [logged_model for logged_model in logged_models
                         if logged_model.source_run_id in logged_models_filter.get(str(logged_model.experiment_id), [])]

    table_data = [ logged_model.name for logged_model in logged_models ]
    columns = ["Logged Model Name"]
    utils.show_table("Logged Models", table_data, columns)

    for logged_model in logged_models:
        _export_logged_model(
            logged_model,
            output_dir,
            mlflow_client,
            ok_logged_models,
            failed_logged_models
        )
        nums_logged_models_exported += 1
        export_results[logged_model.experiment_id]["logged_models"].append(logged_model.model_id)

    info_attr = {
        "num_total_logged_models": (nums_logged_models_exported),
        "num_ok_logged_models": len(ok_logged_models),
        "num_failed_logged_models": len(failed_logged_models),
        "failed_logged_models": failed_logged_models
    }

    mlflow_attr = {"experiments": list(export_results.values())}
    io_utils.write_export_file(output_dir, "logged_models.json", __file__, mlflow_attr, info_attr)

    msg = f"for experiment ids {experiment_ids})"
    if nums_logged_models_exported == 0:
        _logger.warning(f"No logged models exported {msg}")
    elif len(failed_logged_models) == 0:
        _logger.info(f"{len(ok_logged_models)} logged models successfully exported {msg}")
    else:
        _logger.info(f"{len(ok_logged_models)}/{nums_logged_models_exported} logged models successfully exported {msg}")
        _logger.info(f"{len(failed_logged_models)}/{nums_logged_models_exported} logged models failed {msg}")

    return ok_logged_models, failed_logged_models


def _export_logged_model(
        logged_model,
        output_dir,
        mlflow_client,
        ok_logged_models,
        failed_logged_models
    ):
    try:
        _logger.info(f"Exporting logged model: {logged_model.model_id}")

        is_success = export_logged_model(
            model_id=logged_model.model_id,
            output_dir=os.path.join(output_dir, logged_model.model_id),
            mlflow_client=mlflow_client
        )

        if is_success:
            ok_logged_models.append(logged_model.model_id)
        else:
            failed_logged_models.append(logged_model.model_id)

    except RestException as e:
        failed_logged_models.append(logged_model.model_id)
        mlflow_utils.dump_exception(e)
        err_msg = {**{"message": "Cannot export logged model", "logged_model": logged_model.name},
                   **mlflow_utils.mk_msg_RestException(e)}
        _logger.error(err_msg)
    except MlflowExportImportException as e:
        failed_logged_models.append(logged_model.model_id)
        err_msg = {"message": "Cannot export logged model", "logged_model": logged_model.name,
                   "MlflowExportImportException": e.kwargs}
        _logger.error(err_msg)
    except Exception as e:
        failed_logged_models.append(logged_model.model_id)
        err_msg = {"message": "Cannot export logged model", "logged_model": logged_model.name, "Exception": e}
        _logger.error(err_msg)

@click.command()
@opt_experiment_ids
@opt_output_dir
def main(experiment_ids, output_dir):
    _logger.info("Options:")
    for k, v in locals().items():
        _logger.info(f"  {k}: {v}")

    export_logged_models(
        experiment_ids,
        output_dir
    )

if __name__ == "__main__":
    main()