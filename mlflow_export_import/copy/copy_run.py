import click
import tempfile
import mlflow

from mlflow_export_import.run.export_run import export_run
from mlflow_export_import.run.import_run import import_run
from mlflow_export_import.common import utils
from mlflow_export_import.common.click_options import opt_run_id, opt_experiment_name
from . import copy_utils
from . click_options import opt_src_mlflow_uri, opt_dst_mlflow_uri

_logger = utils.getLogger(__name__)


def copy(
        src_run_id, 
        dst_experiment_name, 
        src_mlflow_uri = None, 
        dst_mlflow_uri = None
    ):
    """
    Copies a run to another tracking server (workspace).

    :param src_run_id: Source run ID.
    :param dst_experiment_name: Destination experiment name.
    :param : src_mlflow_uri: Source tracking server (workspace) URI.
    :param : dst_mlflow_uri: Destination tracking server (workspace) URI.

    :return: Destination Run object.
    """

    return _copy(src_run_id, dst_experiment_name, 
        copy_utils.mk_client(src_mlflow_uri), 
        copy_utils.mk_client(dst_mlflow_uri)
    )


def _copy(src_run_id, dst_experiment_name, src_client=None, dst_client=None):
    src_client = src_client or mlflow.MlflowClient()
    dst_client = dst_client or mlflow.MlflowClient()
    with tempfile.TemporaryDirectory() as download_dir:
        export_run(
            src_run_id,
            download_dir,
            notebook_formats = [ "SOURCE" ],
            mlflow_client = src_client
        )
        dst_run, _ = import_run(
            download_dir,
            dst_experiment_name,
            mlflow_client = dst_client
        )
        return dst_run


@click.command()
@opt_run_id
@opt_experiment_name
@opt_src_mlflow_uri
@opt_dst_mlflow_uri
def main(run_id, experiment_name, src_mlflow_uri, dst_mlflow_uri):
    print("Options:")
    for k,v in locals().items():
        print(f"  {k}: {v}")
    copy(run_id, experiment_name, src_mlflow_uri, dst_mlflow_uri)


if __name__ == "__main__":
    main()
