
import click
import os
from packaging import version
import mlflow
import traceback

from mlflow_export_import.client.client_utils import create_mlflow_client
from mlflow_export_import.common import utils, io_utils, mlflow_utils
from mlflow_export_import.common import filesystem as _fs
from mlflow_export_import.common import MlflowExportImportException
from mlflow_export_import.common.click_options import (
    opt_input_dir,
    opt_experiment_name
)
from mlflow_export_import.trace.trace_utils import _get_parent_child_span_graph, _get_span_params
from mlflow_export_import.trace.trace_data_importer import (
    _import_span_data,
    _add_span_events,
    _import_assessments
)
from mlflow_export_import.trace.trace_utils import _try_parse_json, _get_span_attributes

_logger = utils.getLogger(__name__)


def import_trace(
        input_dir,
        experiment_name,
        run_id = None,
        mlflow_client = None,
    ):
    """
    :param input_dir: Input directory
    :param experiment_name: Experiment name
    :param run_id: Run Id
    :param mlflow_client: Mlflow client
    """
    mlflow_client = mlflow_client or create_mlflow_client()

    exp = mlflow_utils.set_experiment(mlflow_client, None, experiment_name)
    src_trace_path = os.path.join(input_dir, "trace.json")
    src_trace_dct = io_utils.read_file_mlflow(src_trace_path)

    dst_trace = None
    try:
        trace_info_dict = src_trace_dct["info"]
        path = _fs.mk_local_path(os.path.join(input_dir, "artifacts"))

        # Trace data is always stored in the artifact store
        if path:
            spans = io_utils.read_spans_data_file(os.path.join(path, "traces.json"))

            # Create a parent-child graph and Span map
            src_graph, src_span_map = _get_parent_child_span_graph(spans)

            # Source Root span
            root_key = None if None in src_graph else ''
            src_root_span = src_span_map[src_graph[root_key][0]]

            # Start trace which creates a root span at destination
            span_params = _get_span_params(src_root_span)
            dst_trace = mlflow_client.start_trace(
                name=src_root_span["name"],
                span_type=_try_parse_json(src_root_span["attributes"].get("mlflow.spanType", "UNKNOWN")),
                inputs=_try_parse_json(src_root_span["attributes"].get("mlflow.spanInputs")),
                attributes=_get_span_attributes(src_root_span["attributes"]),
                tags=trace_info_dict["tags"],
                experiment_id=exp.experiment_id,
                start_time_ns=span_params["start_time_ns"],
            )

            # Import all the child spans
            src_dst_span_map = _import_span_data(
                dst_trace_id = dst_trace.request_id,
                dst_root_span_id = dst_trace.span_id,
                src_root_span_id = src_graph[root_key][0],
                src_graph = src_graph,
                src_span_map = src_span_map,
                mlflow_client = mlflow_client
            )

            # Add span events to the root trace
            _add_span_events(dst_trace, src_root_span.get("events"))

            # Associated run with trace
            trace_metadata = trace_info_dict.get("trace_metadata")
            if trace_metadata is None:
                trace_metadata = trace_info_dict.get("request_metadata")
            if run_id:
                trace_metadata["mlflow.sourceRun"] = run_id
            else:
                # When exporting only traces we skip associating the run with the trace
                trace_metadata.pop("mlflow.sourceRun", None)
            set_trace_metadata(dst_trace.request_id, trace_metadata)

            # End the root trace
            mlflow_client.end_trace(
                request_id = dst_trace.request_id,
                status = span_params['status'],
                attributes = _get_span_attributes(src_root_span['attributes']),
                outputs = _try_parse_json(src_root_span['attributes'].get('mlflow.spanOutputs')),
                end_time_ns = span_params["end_time_ns"],
            )

            #Import assessments. Supported from v3.2
            _import_assessments(trace_info_dict.get("assessments"), dst_trace.request_id, src_dst_span_map)

            _logger.info(f"Successfully imported trace {dst_trace.request_id} to the experiment {experiment_name}")
        else:
            _logger.info("No trace data found to import, skipping the import")
        return dst_trace
    except Exception as e:
        traceback.print_exc()
        raise MlflowExportImportException(e, f"Importing trace {dst_trace.request_id} of experiment '{exp.name}' failed")


def set_trace_metadata(request_id, trace_metadata):
    """Set trace metadata with version compatibility"""
    from mlflow.tracing.trace_manager import InMemoryTraceManager
    tm = InMemoryTraceManager().get_instance()
    exclude_keys = {"mlflow.traceInputs", "mlflow.traceOutputs"}

    for key, value in trace_metadata.items():
        if key in exclude_keys:
            continue

        if version.parse(mlflow.__version__) >= version.parse("3.1.0"):
            # 3.x
            tm.set_trace_metadata(request_id, key, value)
        else:
            # 2.x
            tm.set_request_metadata(request_id, key, value)

@click.command()
@opt_input_dir
@opt_experiment_name
def main(experiment_name, input_dir):
    _logger.info("Options:")
    for k, v in locals().items():
        _logger.info(f"  {k}: {v}")

    import_trace(
        input_dir=input_dir,
        experiment_name = experiment_name,
    )

if __name__ == "__main__":
    main()