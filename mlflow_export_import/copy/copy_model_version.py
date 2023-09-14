import os
import click
import tempfile
import mlflow
from . import local_utils
from . click_options import (
    opt_src_model,
    opt_dst_model,
    opt_src_version,
    opt_src_mlflow_uri,
    opt_dst_mlflow_uri,
    opt_dst_experiment_name
)
from mlflow_export_import.common.source_tags import ExportTags
from mlflow_export_import.common.click_options import opt_verbose
from mlflow_export_import.common import utils
from mlflow_export_import.run import run_utils
from . import uc_utils 

_logger = utils.getLogger(__name__)

def copy(src_model_name, 
        src_model_version, 
        dst_model_name, 
        dst_experiment_name, 
        src_tracking_uri, 
        dst_tracking_uri, 
        src_registry_uri = None, 
        dst_registry_uri = None, 
        verbose = False
    ):
    """
    Copy model version to another model in same or other tracking server (workspace).
    """
    src_client = mlflow.MlflowClient(src_tracking_uri, src_registry_uri)
    dst_client = mlflow.MlflowClient(dst_tracking_uri, dst_registry_uri)

    src_uri = f"{src_model_name}/{src_model_version}"
    print(f"Copying model version '{src_uri}' to '{dst_model_name}'")
    if verbose:
        local_utils.dump_client(src_client, "src_client")
        local_utils.dump_client(dst_client, "dst_client")
    local_utils.create_registered_model(dst_client,  dst_model_name)
    src_version = src_client.get_model_version(src_model_name, src_model_version)
    if verbose:
        local_utils.dump_obj(src_version, "Source ModelVersion")
    dst_version = _copy_model_version(src_version, dst_model_name, dst_experiment_name, src_client, dst_client)
    if verbose:
        local_utils.dump_obj(dst_version, "Destination ModelVersion")
    dst_uri = f"{dst_version.name}/{dst_version.version}"
    print(f"Copied model version '{src_uri}' to '{dst_uri}'")
    return src_version, dst_version


def _copy_model_version(src_version, dst_model_name, dst_experiment_name, src_client, dst_client):
    dst_run = _copy_run(src_version, dst_experiment_name, src_client, dst_client)
    mlflow_model_name = local_utils.get_model_name(src_version.source)
    source_uri = f"{dst_run.info.artifact_uri}/{mlflow_model_name}"
    tags = _add_to_version_tags(src_version, dst_run, dst_model_name, src_client, dst_client)
    dst_version = dst_client.create_model_version(
        name = dst_model_name,
        source = source_uri,
        run_id = dst_run.info.run_id,
        tags = tags,
        description = src_version.description
    )
    for alias in src_version.aliases:
        dst_client.set_registered_model_alias(dst_version.name, alias, dst_version.version)
    if len(src_version.aliases) > 0:
        dst_version = dst_client.get_model_version(dst_version.name, dst_version.version)
    return dst_version


def _copy_run(src_version, dst_experiment_name, src_client, dst_client):
    # If no dst experiment specified, just return src version's run
    if not dst_experiment_name:
        return src_client.get_run(src_version.run_id)

    dst_experiment_id = local_utils.create_experiment(dst_client, dst_experiment_name)
    src_run = src_client.get_run(src_version.run_id)
    tags = { k:v for k,v in src_run.data.tags.items() if not k.startswith("mlflow.") }

    dst_run = dst_client.create_run(dst_experiment_id, tags=tags, run_name=src_run.info.run_name)

    _copy_run_artifacts(src_version, dst_run.info.run_id, src_client, dst_client)
    return dst_run


def _copy_run_artifacts(src_version, dst_run_id, src_client, dst_client):
    with tempfile.TemporaryDirectory() as download_dir:
        mlflow.artifacts.download_artifacts(
            run_id = src_version.run_id,
            dst_path = download_dir,
            tracking_uri = src_client._tracking_client.tracking_uri
        )
        files = os.listdir(download_dir)
        for f in files:
            dst_client.log_artifact(dst_run_id, os.path.join(download_dir, f), artifact_path="")
    run_utils.update_mlmodel_run_id(dst_client, dst_run_id)


def _add_to_version_tags(src_version, run, dst_model_name, src_client, dst_client):
    prefix = f"{ExportTags.PREFIX_ROOT}.src_run"
    if src_version.run_id != run.info.run_id:
        run = src_client.get_run(src_version.run_id)

    tags = src_version.tags
    local_utils.add_tag(run.data.tags, tags, "mlflow.databricks.workspaceURL", prefix)
    local_utils.add_tag(run.data.tags, tags, "mlflow.databricks.webappURL", prefix)
    local_utils.add_tag(run.data.tags, tags, "mlflow.databricks.workspaceID", prefix)
    local_utils.add_tag(run.data.tags, tags, "mlflow.user", prefix)

    tags[f"{ExportTags.PREFIX_ROOT}.src_client.tracking_uri"] = src_client.tracking_uri
    tags[f"{ExportTags.PREFIX_ROOT}.mlflow_exim.dst_client.tracking_uri"] = dst_client.tracking_uri

    if uc_utils.is_unity_catalog_model(dst_model_name): # NOTE: Databricks UC model version tags don't accept '."
        tags = { k.replace(".","_"):v for k,v in tags.items() }

    return tags


@click.command()
@opt_src_model
@opt_src_version
@opt_dst_model
@opt_src_mlflow_uri
@opt_dst_mlflow_uri
@opt_dst_experiment_name
@opt_verbose

def main(src_model, src_version, dst_model, src_mlflow_uri, dst_mlflow_uri, dst_experiment_name, verbose):
    print("Options:")
    for k,v in locals().items():
        print(f"  {k}: {v}")
    copy(src_model, src_version, dst_model, dst_experiment_name, src_mlflow_uri, dst_mlflow_uri, verbose=verbose)


if __name__ == "__main__":
    main()
