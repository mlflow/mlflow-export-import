import mlflow
from mlflow.exceptions import MlflowException


def get_model_name(artifact_path):
    """
    Return 'my-model' from '/foo/artifacts/my-model'
    """
    idx = artifact_path.find("artifacts")
    idx += len("artifacts") + 1
    return artifact_path[idx:]


def create_registered_model(client,  model_name):
    """
    Return True if model already exists, False otherwise.
    """
    try:
        client.create_registered_model(model_name)
        return False
    except MlflowException as e: # NOTE: for non-UC is RestException
        if e.error_code != "RESOURCE_ALREADY_EXISTS":
            raise
        return True


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


def obj_to_dict(obj):
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


def mk_client(tracking_uri, registry_uri=None):
    if not tracking_uri and not registry_uri:
        return mlflow.MlflowClient()
    else:
        tracking_uri = tracking_uri.replace("databricks-uc", "databricks")
        return mlflow.MlflowClient(tracking_uri, registry_uri)
