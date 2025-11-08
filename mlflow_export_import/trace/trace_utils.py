"""
Trace utilities.
"""

import os
import json
from collections import defaultdict
from packaging import version
import mlflow
from mlflow.entities import SpanStatus, SpanStatusCode, Span

from mlflow_export_import.common import filesystem as _fs
from mlflow_export_import.common import io_utils


def _trace_to_json(trace_object):
    result = {}

    # Keeping track of type of Assessment
    if trace_object.__class__.__name__ == "Feedback":
        result["assessment_type"] = "feedback"
    elif trace_object.__class__.__name__ == "Expectation":
        result["assessment_type"] = "expectation"

    for k, v in trace_object.__dict__.items():
        # feedback value is returning true for hasattr which in turn returning null
        if hasattr(v, 'value') and k != "feedback":
            # Handles enums like Status
            result[k] = v.value
        elif isinstance(v, dict):
            result[k] = {key: _try_parse_json(val) if hasattr(val, '__dict__') else val for key, val in v.items()}
        elif hasattr(v, '__dict__'):
            result[k] = _trace_to_json(v)
        elif isinstance(v, list):
            result[k] = [_trace_to_json(item) if hasattr(item, '__dict__') else item for item in v]
        else:
            result[k] = v
    return result

def _extract_span(spans):
    """
    Converts a Spans object to a dictionary with only essential fields. All data in present in traces.json.
    """
    result = []
    for span in spans:
        result.append({
            'name': getattr(span, 'name', None),
            'trace_id': getattr(span, 'trace_id', None),
            'span_id': getattr(span, 'span_id', None),
            'parent_id': getattr(span, 'parent_id', None),
        })
    return result

def _try_parse_json(val):
    if isinstance(val, str):
        try:
            return json.loads(val)
        except (json.JSONDecodeError, ValueError):
            return val
    return val

def _get_parent_child_span_graph(spans):
    graph = defaultdict(list)
    span_map = {}

    for span in spans:
        span_params = _get_span_params(span)
        span_map[span_params["span_id"]] = span
        parent_id = span_params["parent_id"]
        graph[parent_id].append(span_params['span_id'])

    return graph, span_map

def _get_span_attributes(attributes):
    """
    Remove mlflow.* prefixed keys and parse JSON values
    """
    return { k: _try_parse_json(v) for k, v in attributes.items() if not k.startswith('mlflow.') }

def _get_span_params(span_data):
    """
    Get version-specific time parameters
    """
    is_mlflow_3x = version.parse(mlflow.__version__) >= version.parse("3.0.0")

    if is_mlflow_3x and Span._is_span_v2_schema(span_data):
        span_data = Span.from_dict(span_data).to_dict()

    if is_mlflow_3x:
        span_data = Span.from_dict(span_data).to_dict()
        status_code = SpanStatusCode.from_proto_status_code(span_data['status']['code'])
        return {
            "status": SpanStatus(status_code=status_code, description=span_data["status"].get("message", "")),
            "span_id": span_data.get("span_id"),
            "parent_id": span_data.get("parent_span_id"),
            "start_time_ns": span_data.get("start_time_unix_nano"),
            "end_time_ns": span_data.get("end_time_unix_nano"),
            "trace_metadata": span_data.get("trace_metadata"),
        }
    return {
        "status": SpanStatus(status_code=span_data['status_code']),
        "span_id": span_data.get("context", {}).get("span_id"),
        "parent_id": span_data.get("parent_id"),
        "start_time_ns": span_data.get("start_time"),
        "end_time_ns": span_data.get("end_time"),
        "trace_metadata": span_data.get("request_metadata"),
    }


def _write_trace_id_to_run(request_metadata, output_dir, trace_id, experiment_id):
    if request_metadata.get("mlflow.sourceRun") and f"{experiment_id}/runs" in output_dir:
        run_id = request_metadata["mlflow.sourceRun"]
        run_path = output_dir[:output_dir.index("traces")]
        path = _fs.mk_local_path(os.path.join(run_path, "runs", run_id, 'run.json'))
        root_dct = io_utils.read_file(path)
        mlflow_dct = io_utils.get_mlflow(root_dct)

        mlflow_dct.setdefault("traces", []).append(trace_id)
        io_utils.write_file(path, root_dct)