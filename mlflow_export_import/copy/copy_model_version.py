import click
from mlflow.exceptions import MlflowException
from . import copy_run
from . import copy_utils
from . click_options import (
    opt_src_model,
    opt_dst_model,
    opt_src_version,
    opt_src_mlflow_uri,
    opt_dst_mlflow_uri,
    opt_dst_experiment_name,
    opt_add_copy_system_tags
)
from mlflow_export_import.common.source_tags import ExportTags
from mlflow_export_import.common.click_options import opt_verbose
from mlflow_export_import.common import utils

_logger = utils.getLogger(__name__)


def copy(src_model_name,
        src_model_version,
        dst_model_name,
        dst_experiment_name,
        src_tracking_uri = None,
        dst_tracking_uri = None,
        src_registry_uri = None,
        dst_registry_uri = None,
        add_copy_system_tags = False,
        verbose = False
    ):
    """
    Copy model version to another model in same or other tracking server (workspace).
    """
    src_client = copy_utils.mk_client(src_tracking_uri, src_registry_uri)
    dst_client = copy_utils.mk_client(dst_tracking_uri, dst_registry_uri)


    src_uri = f"{src_model_name}/{src_model_version}"
    print(f"Copying model version '{src_uri}' to '{dst_model_name}'")
    if verbose:
        copy_utils.dump_client(src_client, "src_client")
        copy_utils.dump_client(dst_client, "dst_client")
    copy_utils.create_registered_model(dst_client,  dst_model_name)
    src_version = src_client.get_model_version(src_model_name, src_model_version)
    if verbose:
        copy_utils.dump_obj_as_json(src_version, "Source ModelVersion")
    dst_version = _copy_model_version(src_version, dst_model_name, dst_experiment_name, src_client, dst_client, add_copy_system_tags)
    if verbose:
        copy_utils.dump_obj_as_json(dst_version, "Destination ModelVersion")
    dst_uri = f"{dst_version.name}/{dst_version.version}"
    print(f"Copied model version '{src_uri}' to '{dst_uri}'")
    return src_version, dst_version


def _copy_model_version(src_version, dst_model_name, dst_experiment_name, src_client, dst_client, add_copy_system_tags=False):
    if dst_experiment_name:
        dst_run = copy_run._copy(src_version.run_id, dst_experiment_name, src_client, dst_client)
    else:
        dst_run = src_client.get_run(src_version.run_id)

    mlflow_model_name = copy_utils.get_model_name(src_version.source)
    source_uri = f"{dst_run.info.artifact_uri}/{mlflow_model_name}"
    if add_copy_system_tags:
        tags = _add_to_version_tags(src_version, dst_run, dst_model_name, src_client, dst_client)
    else:
        tags = src_version.tags
    copy_utils.dump_client(dst_client, "DST CLIENT")

    dst_version = dst_client.create_model_version(
        name = dst_model_name,
        source = source_uri,
        run_id = dst_run.info.run_id,
        tags = tags,
        description = src_version.description
    )
    try:
        for alias in src_version.aliases:
            dst_client.set_registered_model_alias(dst_version.name, alias, dst_version.version)
        if len(src_version.aliases) > 0:
            dst_version = dst_client.get_model_version(dst_version.name, dst_version.version)
    except MlflowException as e: # Non-UC Databricks MLflow has for some reason removed OSS MLflow support for aliases
        print(f"ERROR: error_code: {e.error_code}. Exception: {e}")
    return dst_version


def _add_to_version_tags(src_version, run, dst_model_name, src_client, dst_client):
    prefix = f"{ExportTags.PREFIX_ROOT}.src_run"
    if src_version.run_id != run.info.run_id:
        run = src_client.get_run(src_version.run_id)

    tags = src_version.tags

    tags[f"{ExportTags.PREFIX_ROOT}.src_version.name"] =  src_version.name
    tags[f"{ExportTags.PREFIX_ROOT}.src_version.version"] =  src_version.version
    tags[f"{ExportTags.PREFIX_ROOT}.src_version.run_id"] =  src_version.run_id

    tags[f"{ExportTags.PREFIX_ROOT}.src_client.tracking_uri"] = src_client.tracking_uri
    tags[f"{ExportTags.PREFIX_ROOT}.mlflow_exim.dst_client.tracking_uri"] = dst_client.tracking_uri

    copy_utils.add_tag(run.data.tags, tags, "mlflow.databricks.workspaceURL", prefix)
    copy_utils.add_tag(run.data.tags, tags, "mlflow.databricks.webappURL", prefix)
    copy_utils.add_tag(run.data.tags, tags, "mlflow.databricks.workspaceID", prefix)
    copy_utils.add_tag(run.data.tags, tags, "mlflow.user", prefix)

    if copy_utils.is_unity_catalog_model(dst_model_name): # NOTE: Databricks UC model version tags don't accept '."
        tags = { k.replace(".","_"):v for k,v in tags.items() }

    return tags


@click.command()
@opt_src_model
@opt_src_version
@opt_dst_model
@opt_src_mlflow_uri
@opt_dst_mlflow_uri
@opt_dst_experiment_name
@opt_add_copy_system_tags
@opt_verbose

def main(src_model, src_version, dst_model, src_mlflow_uri, dst_mlflow_uri, dst_experiment_name, add_copy_system_tags, verbose):
    print("Options:")
    for k,v in locals().items():
        print(f"  {k}: {v}")
    copy(src_model, src_version, dst_model, dst_experiment_name, src_mlflow_uri, dst_mlflow_uri,
        add_copy_system_tags = add_copy_system_tags, 
        verbose = verbose
    )


if __name__ == "__main__":
    main()
