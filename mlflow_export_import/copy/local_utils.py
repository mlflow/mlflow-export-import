import json
from mlflow.exceptions import MlflowException


def get_model_name(artifact_path):
    """
    Return 'my-model' from '/foo/artifacts/my-model'
    """
    idx = artifact_path.find("artifacts")
    idx += len("artifacts") + 1
    return artifact_path[idx:]


def create_registered_model(client,  model_name):
    try:
        client.create_registered_model(model_name)
    except MlflowException as e: # NOTE: for non-UC is RestException
        if e.error_code != "RESOURCE_ALREADY_EXISTS":
            raise


def create_experiment(client, experiment_name):
    try:
        return client.create_experiment(experiment_name)
    except MlflowException as e:
        if e.error_code != "RESOURCE_ALREADY_EXISTS":
            raise
        experiment = client.get_experiment_by_name(experiment_name)
        return experiment.experiment_id


def add_tag(src_tags, dst_tags, key, prefix):
    val = src_tags.get(key)
    if val is not None:
        dst_tags[f"{prefix}.{key}"] = val


def dump_client(client, msg):
    print(f"Mlflow {msg}:")
    print("  client.tracking_uri: ", client.tracking_uri)
    print("  client._registry_uri:", client._registry_uri)


def dump_obj(obj, msg=None):
    title = msg if msg else type(obj).__name__
    print(title)
    for k,v in obj.__dict__.items():
        print(f"  {k}: {v}")


def dump_as_json(dct, sort_keys=None):
    print(json.dumps(dct, sort_keys=sort_keys, indent=2))
