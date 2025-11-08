"""
Import a list of traces from a directory
"""

import os
import click
import mlflow
import traceback

from mlflow_export_import.common.click_options import (
    opt_input_dir
)
from mlflow_export_import.common import utils, io_utils
from mlflow_export_import.trace.import_trace import import_trace

_logger = utils.getLogger(__name__)

def import_traces(
        input_dir,
        mlflow_client = None
    ):
    """
    :param input_dir: Source traces directory
    :param mlflow_client: Mlflow client
    """
    mlflow_client = mlflow_client or mlflow.MlflowClient()
    dct = io_utils.read_file_mlflow(os.path.join(input_dir, "traces.json"))

    exps = dct["experiments"]
    _logger.info(f"Importing traces from {input_dir}")

    for exp in exps:
        _logger.info(f"Importing from experiment: {exp['name']}")
        _logger.info(f"  Importing traces: {exp['traces']}")

    for exp in exps:
        _import_traces(
            exp_name = exp["name"],
            input_dir = input_dir,
            traces = exp["traces"],
            mlflow_client = mlflow_client
        )


def _import_traces(
        exp_name,
        input_dir,
        traces,
        mlflow_client
    ):
    try:
        for trace_id in traces:
            import_trace(
                input_dir = os.path.join(input_dir, trace_id),
                experiment_name = exp_name,
                mlflow_client = mlflow_client
            )
        return traces
    except Exception as e:
        msg = {"experiment": exp_name, "traces": traces, "Exception": str(e)}
        traceback.print_exc()
        _logger.error(f"Failed to import traces: {msg}")
        return None


@click.command()
@opt_input_dir
def main(input_dir):
    _logger.info("Options:")
    for k, v in locals().items():
        _logger.info(f"  {k}: {v}")
    import_traces(input_dir = input_dir)


if __name__ == "__main__":
    main()