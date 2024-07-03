import json
import yaml
import mlflow

def to_json_signature(signature):
    def _to_json(lst):
        return json.loads(lst) if lst else lst
    return { k:_to_json(v) for k,v in signature.items()}


def get_model_signature(model_uri, use_get_model_info=False):
    """
    Return a fully exploded dict of of the stringified JSON signature field of MLmodel.
    :param use_get_model_info: Use mlflow.models.get_model_info() which apparently downloads *all* artifacts (quite slow for large models) instead of just downloading 'MLmodel' using mlflow.artifacts.download_artifacts().
    :return: Returns signature as dictionary..
    """
    if use_get_model_info:
        return get_model_signature_use_get_model_info(model_uri)
    else:
        return get_model_signature_use_download_MLmodel(model_uri)

def get_model_signature_use_download_MLmodel(model_uri):
    artifact_uri = f"{model_uri}/MLmodel"
    local_path = mlflow.artifacts.download_artifacts(artifact_uri)
    with open(local_path, "r") as f:
        mlmodel = yaml.safe_load(f)
        sig = mlmodel.get("signature")
        return to_json_signature(sig) if sig else None

def get_model_signature_use_get_model_info(model_uri):
    model_info = mlflow.models.get_model_info(model_uri)
    if model_info.signature:
        sig =  model_info.signature.to_dict()
        return to_json_signature(sig)
    else:
        return None
