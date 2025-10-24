
from mlflow.entities import Metric, Dataset, DatasetInput, InputTag


def _log_metrics(mlflow_client, run_id, logged_model_metrics_dict, model_id):
    metrics = []

    for metric in logged_model_metrics_dict:
        metrics.append(Metric(
            key = metric["key"],
            value = metric["value"],
            timestamp = metric["timestamp"],
            step = metric["step"],
            model_id = model_id,
            dataset_name = metric["dataset_name"],
            dataset_digest = metric["dataset_digest"],
        ))
    mlflow_client.log_batch(run_id, metrics=metrics)


def _import_inputs(mlflow_client, src_run_dct, run_id):
    inputs = src_run_dct.get("dataset_inputs", [])
    if not inputs:
        return
    dataset_inputs = [DatasetInput(Dataset.from_dictionary(input['dataset']), [InputTag.from_dictionary(tag) for tag in input['tags']]) for input in inputs]
    mlflow_client.log_inputs(run_id=run_id, datasets=dataset_inputs)
