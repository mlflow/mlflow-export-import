"""
Exports traces to a Directory.
"""

import os
import click
import mlflow
from mlflow.exceptions import RestException

from mlflow_export_import.common.click_options import (
    opt_experiment_ids,
    opt_output_dir
)
from mlflow_export_import.common import MlflowExportImportException
from mlflow_export_import.bulk.bulk_utils import get_experiment_ids, get_traces
from mlflow_export_import.common import utils, mlflow_utils, io_utils
from mlflow_export_import.trace.export_trace import export_trace

_logger = utils.getLogger(__name__)

def export_traces(
        experiment_ids,
        output_dir,
        run_id = None,
        mlflow_client = None,
    ):
    """
    :param experiment_ids: can be either:
      - List of Experiment Ids
      - String with comma-delimited experiment IDs such as '1,2' or 'all'
    :param output_dir: Directory where logged models will be exported
    :param run_id: Run id to filter during search
    :param mlflow_client: Mlflow client
    """

    mlflow_client = mlflow_client or mlflow.MlflowClient()
    if isinstance(experiment_ids, str):
        experiment_ids = get_experiment_ids(mlflow_client, experiment_ids)

    ok_traces = []
    failed_traces = []
    nums_traces_exported = 0

    export_results = {
        exp_id: {
            "id": exp_id,
            "name": mlflow_client.get_experiment(exp_id).name,
            "traces": []} for exp_id in experiment_ids
    }

    try:
        traces = get_traces(mlflow_client, experiment_ids, run_id)

        if len(traces) == 0:
            _logger.info(f"No traces found for experiment ids {experiment_ids})")
            return ok_traces, failed_traces

        table_data = [trace.info.request_id for trace in traces]
        columns = ["Trace Name"]
        utils.show_table("Traces", table_data, columns)

        for trace in traces:
            _export_trace(
                trace.info.request_id,
                output_dir,
                mlflow_client,
                ok_traces,
                failed_traces,
            )
            nums_traces_exported += 1
            export_results[trace.info.experiment_id]["traces"].append(trace.info.request_id)

        info_attr = {
            "num_total_trace": nums_traces_exported,
            "num_ok_traces": len(ok_traces),
            "num_failed_traces": len(failed_traces),
            "failed_traces": failed_traces,
        }
        mlflow_attr = {"experiments": list(export_results.values())}
        io_utils.write_export_file(output_dir, "traces.json", __file__, mlflow_attr, info_attr)
        msg = f"for experiment ids {experiment_ids})"

        if nums_traces_exported == 0:
            _logger.warning(f"No traces exported {msg}")
        elif len(failed_traces) == 0:
            _logger.info(f"{len(ok_traces)} traces successfully exported {msg}")
        else:
            _logger.info(f"{len(ok_traces)}/{nums_traces_exported} traces successfully exported {msg}")
            _logger.info(f"{len(failed_traces)}/{nums_traces_exported} traces failed {msg}")
    except Exception as e:
        err_msg = {"for experiment_ids": experiment_ids, "Exception": e}
        _logger.error(f"Traces export failed (2): {err_msg}")
    return ok_traces, failed_traces


def _export_trace(
        request_id,
        output_dir,
        mlflow_client,
        ok_traces,
        failed_traces,
    ):

    try:
        _logger.info(f"Exporting trace for experiment {request_id}")
        is_success = export_trace(
            request_id=request_id,
            output_dir=os.path.join(output_dir, request_id),
            mlflow_client = mlflow_client
        )

        if is_success:
            ok_traces.append(request_id)
        else:
            failed_traces.append(request_id)

    except RestException as e:
        failed_traces.append(request_id)
        mlflow_utils.dump_exception(e)
        err_msg = {**{"message": "Cannot export trace", "trace_id": request_id,},
                   **mlflow_utils.mk_msg_RestException(e)}
        _logger.error(err_msg)
    except MlflowExportImportException as e:
        failed_traces.append(request_id)
        err_msg = {"message": "Cannot export trace", "trace_id": request_id,
                   "MlflowExportImportException": e.kwargs}
        _logger.error(err_msg)
    except Exception as e:
        failed_traces.append(request_id)
        err_msg = {"message": "Cannot export trace", "trace_id": request_id, "Exception": e}
        _logger.error(err_msg)


@click.command()
@opt_experiment_ids
@opt_output_dir
def main(experiment_ids, output_dir):
    _logger.info("Options:")
    for k, v in locals().items():
        _logger.info(f"  {k}: {v}")

    export_traces(
        experiment_ids,
        output_dir
    )

if __name__ == "__main__":
    main()