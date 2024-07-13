"""
Module to handle importing MLflow run data (params, metrics and tags).
Focus is on data that exceed API limits.
See: https://www.mlflow.org/docs/latest/rest-api.html#request-limits.
"""

import math
import mlflow
from mlflow.entities import Metric, Param, RunTag

from mlflow_export_import.common import utils
from mlflow_export_import.common.source_tags import ExportTags
from mlflow_export_import.common.source_tags import mk_source_tags_mlflow_tag, mk_source_tags


def _log_data(run_dct, run_id, batch_size, get_data, log_data, args_get_data=None):
    metadata = get_data(run_dct, args_get_data)
    num_batches = int(math.ceil(len(metadata) / batch_size))
    res = []
    for j in range(num_batches):
        start = j * batch_size
        end = start + batch_size
        batch = metadata[start:end]
        log_data(run_id, batch)
        res = res + batch


def _log_params(client, run_dct, run_id, batch_size):
    def get_data(run_dct, args):
        return [ Param(k,v) for k,v in run_dct["params"].items() ]
    def log_data(run_id, params):
        client.log_batch(run_id, params=params)
    _log_data(run_dct, run_id, batch_size, get_data, log_data)


def _log_metrics(client, run_dct, run_id, batch_size):

    def get_data(run_dct, args=None):
        metrics = []
        for metric,steps in  run_dct["metrics"].items():
            for step in steps:
                metrics.append(Metric(metric,step["value"],step["timestamp"],step["step"]))
        return metrics

    def log_data(run_id, metrics):
        client.log_batch(run_id, metrics=metrics)

    _log_data(run_dct, run_id, batch_size, get_data, log_data)


def _log_tags(client, run_dct, run_id, batch_size, import_source_tags, in_databricks, src_user_id, use_src_user_id):

    def get_data(run_dct, args):
        tags = run_dct["tags"]
        if import_source_tags:
            source_mlflow_tags = mk_source_tags_mlflow_tag(tags)
            info =  run_dct["info"]
            source_info_tags = mk_source_tags(info, f"{ExportTags.PREFIX_RUN_INFO}")
            tags = { **tags, **source_mlflow_tags, **source_info_tags }
        tags = utils.create_mlflow_tags_for_databricks_import(tags) # remove "mlflow" tags that cannot be imported into Databricks
        tags = [ RunTag(k,v) for k,v in tags.items() ]
        if not in_databricks:
            utils.set_dst_user_id(tags, args["src_user_id"], args["use_src_user_id"])
        return tags

    def log_data(run_id, tags):
        client.log_batch(run_id, tags=tags)

    args_get = {
        "in_databricks": in_databricks,
        "src_user_id": src_user_id,
        "use_src_user_id": use_src_user_id
    }

    _log_data(run_dct, run_id, batch_size, get_data, log_data, args_get)


def import_run_data(mlflow_client, run_dct, run_id, import_source_tags, src_user_id, use_src_user_id, in_databricks):
    from mlflow.utils.validation import MAX_PARAMS_TAGS_PER_BATCH, MAX_METRICS_PER_BATCH
    _log_params(mlflow_client, run_dct, run_id, MAX_PARAMS_TAGS_PER_BATCH)
    _log_metrics(mlflow_client, run_dct, run_id, MAX_METRICS_PER_BATCH)
    _log_tags(
        mlflow_client,
        run_dct,
        run_id,
        MAX_PARAMS_TAGS_PER_BATCH,
        import_source_tags,
        in_databricks,
        src_user_id,
        use_src_user_id
)


if __name__ == "__main__":
    import sys
    client = mlflow.MlflowClient()
    _log_metrics(client, sys.argv[1],100)
