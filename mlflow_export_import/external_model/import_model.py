"""
Imports an already trained model into MLflow.
"""

import click
import mlflow
from mlflow.exceptions import RestException

from mlflow_export_import.common import utils, io_utils
from mlflow_export_import.common.click_options import opt_experiment
from . import model_handlers

_logger = utils.getLogger(__name__)
client = mlflow.MlflowClient()


def import_model(model_path,
        experiment_name,
        flavor,
        log_import_metadata_tags = False,
        config_path = "config.yaml"
    ):
    cfg = _read_conf(config_path)
    model_handler = model_handlers.get_model_handler(flavor)
    _logger.info(f"model_handler: {model_handler}")

    _create_experiment(experiment_name, cfg.get("experiment",{}))
    run = _create_run(model_handler, model_path, flavor, log_import_metadata_tags, cfg.get("run",{}))
    _logger.info(f"run_id: {run.info.run_id}")
    _logger.info(f"experiment_id: {run.info.experiment_id}")
    _logger.info(f"experiment_name: {experiment_name}")

    return run


def _create_run(model_handle, model_path, flavor, log_import_metadata_tags, cfg=None):
    cfg = cfg if cfg else {}
    run_name = cfg.get("name")
    tags = cfg.get("tags")
    desc = cfg.get("description")
    params = cfg.get("params")
    metrics = cfg.get("metrics")

    with mlflow.start_run(run_name=run_name) as run:
        print("run_id:",run.info.run_id)
        model = model_handle.load_model(model_path)
        model_handle.log_model(model, "model")
        if params:
            mlflow.log_params(params)
        if metrics:
            mlflow.log_metrics(metrics)
        if tags:
            mlflow.set_tags(tags)
        if desc:
            mlflow.set_tag("mlflow.note.content", desc)
        if log_import_metadata_tags:
            _log_import_metadata_tags(model, model_path, flavor)
    return run


def _log_import_metadata_tags(model, model_path, flavor):
    def _tweak_tag(key):
        return f"mlflow_exim.{key}"
    mlflow.set_tag(_tweak_tag("model_path"), model_path)
    mlflow.set_tag(_tweak_tag("model.type"), model.__class__)
    mlflow.set_tag(_tweak_tag("model"), model)
    mlflow.set_tag(_tweak_tag("flavor"), flavor)


def _create_experiment(experiment_name, cfg):
    try:
        tags = cfg.get("tags", {})
        desc = cfg.get("description")
        if desc:
            tags["mlflow.note.content"] =  desc
        mlflow.create_experiment(experiment_name,
            artifact_location = cfg.get("artifact_location"),
            tags = tags
        )
    except RestException:
        pass
    mlflow.set_experiment(experiment_name)


def _read_conf(config_path):
    import os
    if os.path.exists(config_path):
        cfg = io_utils.read_file(config_path)
    else:
        print(f"WARNING: Config file '{config_path}' does not exists")
        cfg = {}
    return cfg


@click.command()
@click.option("--model-path",
    help="Path to native model artifacts.",
    type=str,
    required=True
)
@opt_experiment
@click.option("--flavor",
    help="MLflow model flavor.",
    type=str,
    required=True
)
@click.option("--log-import-metadata-tags",
    help="Log import metadata tags",
    type=bool,
    default=False
)
@click.option("--config-path",
    help="Config file.",
    type=str,
    default="config.yaml"
)

def main(model_path,
        experiment,
        flavor,
        log_import_metadata_tags,
        config_path,
    ):
    _logger.info("Options:")
    for k,v in locals().items():
        _logger.info(f"  {k}: {v}")
    import_model(
        model_path,
        experiment,
        flavor,
        log_import_metadata_tags,
        config_path
     )


if __name__ == "__main__":
    main()
