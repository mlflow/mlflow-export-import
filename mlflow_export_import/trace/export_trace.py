"""
Export a trace to a directory
"""

import click
import traceback
import time
import mlflow
from mlflow.exceptions import RestException, MlflowException

from mlflow_export_import.client.client_utils import create_mlflow_client
from mlflow_export_import.common import filesystem as _fs
from mlflow_export_import.common import utils, io_utils
from mlflow_export_import.common.click_options import (
    opt_request_id,
    opt_output_dir
)
from mlflow_export_import.common.timestamp_utils import format_seconds
from mlflow_export_import.trace.trace_utils import (
    _trace_to_json,
    _extract_span,
    _write_trace_id_to_run
)

_logger = utils.getLogger(__name__)

def export_trace(
        request_id,
        output_dir,
        mlflow_client = None,
    ):
    """
    :param request_id: The trace request id
    :param output_dir: Output directory
    :param mlflow_client: Mlflow client
    """
    mlflow_client = mlflow_client or create_mlflow_client()
    experiment_id = None
    start_time = time.time()

    try:
        trace = mlflow_client.get_trace(request_id)
        experiment_id = trace.info.experiment_id
        msg = {"trace_id": request_id, "experiment_id": experiment_id}
        _logger.info(f"Exporting trace: {msg}")

        mlflow_attr = {
            "info": _trace_to_json(trace.info),
            "data": _extract_span(trace.data.spans)
        }
        io_utils.write_export_file(output_dir, "trace.json", __file__, mlflow_attr)

        # Add trace_id to run metadata if found
        _write_trace_id_to_run(trace.info.request_metadata, output_dir, trace.info.request_id, experiment_id)

        # Trace data is always stored in the artifact location
        if "mlflow.artifactLocation" in trace.info.tags:
            artifacts = mlflow.artifacts.list_artifacts(artifact_uri = trace.info.tags["mlflow.artifactLocation"])

            if len(artifacts) > 0:
                mlflow.artifacts.download_artifacts(
                    artifact_uri = trace.info.tags["mlflow.artifactLocation"],
                    dst_path = _fs.mk_local_path(output_dir),
                    tracking_uri = mlflow_client._tracking_client.tracking_uri
                )

        dur = format_seconds(time.time() - start_time)
        _logger.info(f"Exported trace in {dur}: {msg}")
        return trace
    except RestException as e:
        err_msg = {"request_id": request_id, "experiment_id": experiment_id, "RestException": e.json}
        _logger.error(f"Trace export failed (1): {err_msg}")
        return None
    except MlflowException as e:
        err_msg = {"request_id": request_id, "experiment_id": experiment_id, "MlflowException": e}
        _logger.error(f"Trace export failed (1): {err_msg}")
        return None
    except Exception as e:
        err_msg = {"request_id": request_id, "experiment_id": experiment_id, "Exception": e}
        _logger.error(f"Trace export failed (2): {err_msg}")
        traceback.print_exc()
        return None


@click.command()
@opt_request_id
@opt_output_dir
def main(request_id, output_dir):
    _logger.info("Options:")
    for k, v in locals().items():
        _logger.info(f"  {k}: {v}")

    export_trace(
        request_id=request_id,
        output_dir=output_dir,
    )

if __name__ == "__main__":
    main()