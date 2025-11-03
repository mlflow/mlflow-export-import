"""
Functions to import trace data
"""
import base64
import mlflow
from packaging import version
from mlflow.entities import SpanEvent, Feedback, Expectation, AssessmentSource, AssessmentError, Span

from mlflow_export_import.trace.trace_utils import (
    _try_parse_json,
    _get_span_attributes,
    _get_span_params
)


def _import_span_data(dst_trace_id, dst_root_span_id, src_root_span_id, src_graph, src_span_map, mlflow_client):
    """
    Approach: BFS (Queue + Visited list)
    """
    # Useful for Assessment logging
    src_dst_span_map = {decode_span_id(src_root_span_id): dst_root_span_id}
    span_queue = []

    # Parent Span children - For parent we already started a trace which automatically creates a span
    for src_child_span_id in src_graph[src_root_span_id]:
        span_queue.append((src_child_span_id, dst_root_span_id))

    visited_span = set()
    visited_span.add(src_root_span_id) # Add parent span id to visited

    while len(span_queue) > 0:
        src_span_id, dst_span_parent_id = span_queue.pop(0)

        # We will be traversing DAG. This is safeguard to avoid any infinite loop
        if src_span_id in visited_span:
            continue

        # Mark as visited
        visited_span.add(src_span_id)

        span_data = src_span_map[src_span_id]
        span_params = _get_span_params(span_data)

        # Create a parent span
        dst_child_span = mlflow_client.start_span(
            name=span_data["name"],
            request_id=dst_trace_id,
            parent_id=dst_span_parent_id,
            span_type=_try_parse_json(span_data["attributes"].get("mlflow.spanType", "UNKNOWN")),
            inputs=_try_parse_json(span_data['attributes'].get("mlflow.spanInputs")),
            attributes=_get_span_attributes(span_data['attributes']),
            start_time_ns=span_params['start_time_ns'],
        )

        # End the current parent span
        mlflow_client.end_span(
            request_id=dst_trace_id,
            span_id=dst_child_span.span_id,
            status=span_params['status'],
            outputs=_try_parse_json(span_data['attributes'].get("mlflow.spanOutputs")),
            end_time_ns=span_params['end_time_ns'],
        )
        src_dst_span_map[decode_span_id(src_span_id)] = dst_child_span.span_id

        # Add its child spans to the Queue along with the new parent span id
        for src_child_span_id in src_graph[src_span_id]:
            span_queue.append((src_child_span_id, dst_child_span.span_id))

    return src_dst_span_map


def _add_span_events(dst_child_span, span_events):
    if span_events and len(span_events) > 0:
        for span_event in span_events:
            dst_child_span.add_event(SpanEvent(
                name=span_event["name"],
                timestamp=span_event.get("timestamp") or span_event.get("time_unix_nano"),
                attributes=span_event["attributes"],
            ))

def _import_assessments(assessments, trace_id, src_dst_span_map):
    if version.parse(mlflow.__version__) >= version.parse("3.4.0"):
        for assessment in assessments:

            assessment_input = {
                "name": assessment["name"],
                "source": AssessmentSource(
                    source_type = assessment.get("source").get("source_type"),
                    source_id = assessment.get("source").get("source_id")
                ),
                "trace_id": trace_id,
                "span_id": src_dst_span_map.get(assessment["span_id"]),
                "metadata": assessment["metadata"],
                "create_time_ms": assessment["create_time_ms"],
                "last_update_time_ms": assessment["last_update_time_ms"]
            }

            if assessment.get("assessment_type") == "feedback":
                assessment_input["error"] = AssessmentError(error_code=assessment.get("error")["error_code"],
                                         error_message=assessment.get("error")["error_message"],
                                         stack_trace=assessment.get("error")["stack_trace"]) if assessment.get("error") else None
                assessment_input["rationale"] = str(assessment["rationale"])
                assessment_input["overrides"] = assessment["overrides"]
                assessment_input["valid"] = assessment["valid"]
                assessment_input["value"] = assessment["feedback"]["value"]
                final_assessment = Feedback(**assessment_input)
            elif assessment.get("assessment_type") == "expectation":
                assessment_input["value"] = assessment["expectation"]
                final_assessment = Expectation(**assessment_input)

            mlflow.log_assessment(trace_id=trace_id, assessment=final_assessment)

# https://github.com/mlflow/mlflow/blob/master/mlflow/entities/span.py#L272
def decode_span_id(span_id):
    try:
        bytes_data = base64.b64decode(span_id, validate=True)
        return bytes_data.hex()
    except Exception:
        return int(span_id, 16)