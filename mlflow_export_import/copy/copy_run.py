import os
import click
import tempfile
import mlflow


from mlflow_export_import.common.click_options import opt_run_id
from mlflow_export_import.common import utils
from mlflow_export_import.run import run_utils
from . import local_utils
from . click_options import (
    opt_dst_experiment_name,
    opt_src_mlflow_uri,
    opt_dst_mlflow_uri,
)

_logger = utils.getLogger(__name__)


def copy(src_run_id, dst_experiment_name, src_mlflow_uri, dst_mlflow_uri):
    return _copy(src_run_id, dst_experiment_name, 
        mlflow.MlflowClient(src_mlflow_uri, src_mlflow_uri),
        mlflow.MlflowClient(dst_mlflow_uri, dst_mlflow_uri)
    )


def _copy(src_run_id, dst_experiment_name, src_client, dst_client):
    local_utils.dump_client(src_client, "src_client")
    local_utils.dump_client(dst_client, "dst_client")
    # If no dst experiment specified, just return src version's run
    if not dst_experiment_name:
        return src_client.get_run(src_run_id)

    dst_experiment_id = local_utils.create_experiment(dst_client, dst_experiment_name)
    src_run = src_client.get_run(src_run_id)
    tags = { k:v for k,v in src_run.data.tags.items() if not k.startswith("mlflow.") }

    dst_run = dst_client.create_run(dst_experiment_id, tags=tags, run_name=src_run.info.run_name)
    dst_client.set_terminated(dst_run.info.run_id, src_run.info.status)

    for k,v in src_run.data.params.items():
        dst_client.log_param(dst_run.info.run_id, k, v)
    for k,v in src_run.data.metrics.items():
        dst_client.log_metric(dst_run.info.run_id, k, v)

    _copy_run_artifacts(src_run.info.run_id, dst_run.info.run_id, src_client, dst_client)

    return dst_client.get_run(dst_run.info.run_id)


def _copy_run_artifacts(src_run_id, dst_run_id, src_client, dst_client):
    with tempfile.TemporaryDirectory() as download_dir:
        mlflow.artifacts.download_artifacts(
            run_id = src_run_id,
            dst_path = download_dir,
            tracking_uri = src_client._tracking_client.tracking_uri
        )
        files = os.listdir(download_dir)
        for f in files:
            dst_client.log_artifact(dst_run_id, os.path.join(download_dir, f), artifact_path="")
    run_utils.update_mlmodel_run_id(dst_client, dst_run_id)


@click.command()
@opt_run_id
@opt_dst_experiment_name
@opt_src_mlflow_uri
@opt_dst_mlflow_uri
def main(run_id, dst_experiment_name, src_mlflow_uri, dst_mlflow_uri):
    print("Options:")
    for k,v in locals().items():
        print(f"  {k}: {v}")
    copy(run_id, dst_experiment_name, src_mlflow_uri, dst_mlflow_uri)


if __name__ == "__main__":
    main()
