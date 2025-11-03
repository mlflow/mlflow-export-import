"""
Imports an experiment to a directory.
"""

import os
import click

from mlflow_export_import.common.click_options import (
    opt_experiment_name,
    opt_input_dir,
    opt_import_source_tags,
    opt_import_permissions,
    opt_use_src_user_id,
    opt_dst_notebook_dir
)
from mlflow_export_import.client.client_utils import create_mlflow_client, create_dbx_client
from mlflow_export_import.common import utils, mlflow_utils, io_utils
from mlflow_export_import.common import ws_permissions_utils
from mlflow_export_import.common.source_tags import (
    set_source_tags_for_field,
    mk_source_tags_mlflow_tag,
    fmt_timestamps
)
from mlflow_export_import.run.import_run import import_run
from mlflow_export_import.logged_model.import_logged_model import import_logged_model
from mlflow_export_import.trace.import_trace import import_trace

_logger = utils.getLogger(__name__)


def import_experiment(
        experiment_name,
        input_dir,
        import_source_tags = False,
        import_permissions = False,
        use_src_user_id = False,
        dst_notebook_dir = None,
        mlflow_client = None
    ):
    """
    :param experiment_name: Destination experiment name.
    :param input_dir: Source experiment directory.
    :param import_source_tags: Import source information for MLflow objects and create tags in destination object.
    :param import_permissions: Import Databricks permissions.
    :param use_src_user_id: Set the destination user ID to the source user ID.
                            Source user ID is ignored when importing into Databricks.
    :param dst_notebook_dir: Destination Databricks workspace directory if importing notebook.
    :param mlflow_client: MLflow client.
    :return: Dictionary of source run_id (key) to destination run.info object (value).
    """

    mlflow_client = mlflow_client or create_mlflow_client()
    dbx_client = create_dbx_client(mlflow_client)

    path = io_utils.mk_manifest_json_path(input_dir, "experiment.json")
    root_dct = io_utils.read_file(path)
    info = io_utils.get_info(root_dct)
    mlflow_dct = io_utils.get_mlflow(root_dct)
    exp_dct = mlflow_dct["experiment"]

    tags = exp_dct["tags"]
    if import_source_tags:
        source_tags = mk_source_tags_mlflow_tag(tags)
        tags = { **tags, **source_tags }
        exp = mlflow_dct["experiment"]
        set_source_tags_for_field(exp, tags)
        fmt_timestamps("creation_time", exp, tags)
        fmt_timestamps("last_update_time", exp, tags)

    exp = mlflow_utils.set_experiment(mlflow_client, dbx_client, experiment_name, tags)

    if import_permissions:
        perms_dct = mlflow_dct.get("permissions", None)
        if perms_dct:
            ws_permissions_utils.update_permissions(dbx_client, perms_dct, "experiment", exp.name, exp.experiment_id)

    run_ids = mlflow_dct["runs"]
    failed_run_ids = info["failed_runs"]

    _logger.info(f"Importing {len(run_ids)} runs into experiment '{experiment_name}' from '{input_dir}'")
    run_ids_map = {}
    run_info_map = {}
    imported_logged_models = []
    imported_traces = []
    for src_run_id in run_ids:
        dst_run, src_parent_run_id = import_run(
            mlflow_client = mlflow_client,
            experiment_name = experiment_name,
            input_dir = os.path.join(input_dir, f'runs/{src_run_id}'),
            dst_notebook_dir = dst_notebook_dir,
            import_source_tags = import_source_tags,
            use_src_user_id = use_src_user_id
        )
        dst_run_id = dst_run.info.run_id
        run_ids_map[src_run_id] = { "dst_run_id": dst_run_id, "src_parent_run_id": src_parent_run_id }
        run_info_map[src_run_id] = dst_run.info

        src_run_dct = io_utils.read_file_mlflow(os.path.join(input_dir, f'runs/{src_run_id}/run.json'))

        # Logged Models
        if "model_inputs" in src_run_dct["inputs"]:
            for model in src_run_dct["inputs"]["model_inputs"]:
                import_logged_model(
                    input_dir = os.path.join(f"{input_dir}/logged_models", model['model_id']),
                    experiment_name = experiment_name,
                    run_id = dst_run_id,
                    mlflow_client = mlflow_client,
                    model_type = "input",
                    step = model['step'],
                )
                imported_logged_models.append(model['model_id'])

        if "outputs" in src_run_dct:
            for model in src_run_dct["outputs"]["model_outputs"]:
                import_logged_model(
                    input_dir = os.path.join(f"{input_dir}/logged_models", model['model_id']),
                    experiment_name = experiment_name,
                    run_id = dst_run_id,
                    mlflow_client = mlflow_client,
                    model_type = "output",
                    step = model['step'],
                )
                imported_logged_models.append(model['model_id'])

        # Import traces associated to the run
        if src_run_dct.get("traces"):
            for trace_id in src_run_dct["traces"]:
                import_trace(
                    input_dir=os.path.join(f"{input_dir}/traces", trace_id),
                    experiment_name=experiment_name,
                    run_id=dst_run_id,
                    mlflow_client=mlflow_client,
                )
                imported_traces.append(trace_id)

    ## Importing the logged models that are not part of run
    if "logged_models" in mlflow_dct:
        remaining_logged_models = set(mlflow_dct["logged_models"]) - set(imported_logged_models)
        for model_id in remaining_logged_models:
            import_logged_model(
                input_dir=os.path.join(f"{input_dir}/logged_models", model_id),
                experiment_name=experiment_name,
                mlflow_client=mlflow_client,
            )

    ## Importing the traces that are not part of run
    if mlflow_dct.get("traces"):
        remaining_traces = set(mlflow_dct["traces"]) - set(imported_traces)
        for trace_id in remaining_traces:
            import_trace(
                input_dir=os.path.join(f"{input_dir}/traces", trace_id),
                experiment_name=experiment_name,
                mlflow_client=mlflow_client,
            )

    _logger.info(f"Imported {len(run_ids)} runs into experiment '{experiment_name}' from '{input_dir}'")
    if len(failed_run_ids) > 0:
        _logger.warning(f"{len(failed_run_ids)} failed runs were not imported - see '{path}'")
    utils.nested_tags(mlflow_client, run_ids_map)

    return run_info_map


@click.command()
@opt_experiment_name
@opt_input_dir
@opt_import_permissions
@opt_import_source_tags
@opt_use_src_user_id
@opt_dst_notebook_dir

def main(input_dir, experiment_name, import_source_tags, use_src_user_id, dst_notebook_dir, import_permissions):
    _logger.info("Options:")
    for k,v in locals().items():
        _logger.info(f"  {k}: {v}")
    import_experiment(
        experiment_name = experiment_name,
        input_dir = input_dir,
        import_source_tags = import_source_tags,
        import_permissions = import_permissions,
        use_src_user_id = use_src_user_id,
        dst_notebook_dir = dst_notebook_dir
    )


if __name__ == "__main__":
    main()
