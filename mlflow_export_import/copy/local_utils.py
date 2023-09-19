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


def is_unity_catalog_model(name):
    return len(name.split(".")) == 3


def dump_client(client, msg=""):
    print(f"Mlflow {msg}:")
    print("  client.tracking_uri: ", client.tracking_uri)
    print("  client._registry_uri:", client._registry_uri)


def dump_obj(obj, msg=None):
    title = msg if msg else type(obj).__name__
    print(title)
    for k,v in obj.__dict__.items():
        print(f"  {k}: {v}")


def dump_obj_as_json(obj, msg=None):
    title = msg if msg else type(obj).__name__
    print(title)
    dct = obj_to_dict(obj)
    dump_as_json(dct)


def dump_as_json(dct, sort_keys=None, indent=2):
    print(dict_to_json(dct, sort_keys, indent))


def dict_to_json(dct, sort_keys=None, indent=2):
    return json.dumps(dct, sort_keys=sort_keys, indent=indent)


def obj_to_dict(obj):
    import mlflow
    if isinstance(obj, mlflow.entities.model_registry.model_version.ModelVersion):
        dct = adjust_model_version(obj.__dict__)
    else:
        dct = obj.__dict__
    return dct


def adjust_model_version(vr):
    dct = {}
    for k,v in vr.items():
        if k == "_aliases": # type - google._upb._message.RepeatedScalarContainer
            dct[k] = [ str(x) for x in v ]
        else:
            dct[k] = v
    return dct
