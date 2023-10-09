"""
Model handlers for a few popular MLflow flavors.

A "Model Handler" object has two methods:
  1. load_model - loads the native model using the native model's API
  2. log_model - logs this loaded native model as an MLflow model flavor

"""

import mlflow

def _load_sklearn_model(path):
    import cloudpickle as pickle
    with open(path, "rb") as f:
        model = pickle.load(f)
    return model

def _load_xgboost_model(path):
    from mlflow.xgboost import _load_model
    return _load_model(path)

def _load_sparkml_model(path):
    from pyspark.ml.pipeline import PipelineModel
    return PipelineModel.load(path)

def _load_tensorflow_model(path):
    import tensorflow as tf
    return tf.keras.models.load_model(path)

def _load_pytorch_model(path):
    from mlflow.pytorch import _load_model
    return _load_model(path)


from dataclasses import dataclass
@dataclass(frozen=True)
class ModelHandler:
    load_model: None
    log_model: None


_model_handlers = {
    "sklearn":    ModelHandler(_load_sklearn_model,    mlflow.sklearn.log_model),
    "xgboost":    ModelHandler(_load_xgboost_model,    mlflow.xgboost.log_model),
    "sparkml":    ModelHandler(_load_sparkml_model,    mlflow.spark.log_model),
    "tensorflow": ModelHandler(_load_tensorflow_model, mlflow.tensorflow.log_model),
    "pytorch":    ModelHandler(_load_pytorch_model,    mlflow.pytorch.log_model)
}


def _load_model_handler(module_path):
    """
    Loads ModelHandle for the specified custom model path.
    :param module_path - Path to Python file containing native logic to load the model
    :returns: ModelHandle for the custom model
    """
    import runpy
    dct = runpy.run_path(module_path)
    func_name = "get_model_handler"
    func = dct.get(func_name)
    if not func:
        raise TypeError(f"Cannot find function '{func_name}' in '{module_path}'")
    obj = func()
    if not isinstance(obj,ModelHandler):
        raise TypeError(f"Object {type(obj)} is not of type {ModelHandler}")
    return obj


def get_model_handler(flavor_or_file):
    """
    Get ModelHandle for specified flavor.
    :flavor_or_file MLflow model flavor name or Python file containing custom model handler logic
    :returns: ModelHandle for specified flavor
    """
    if flavor_or_file.endswith(".py"):
        return _load_model_handler(flavor_or_file)
    else:
        handler = _model_handlers.get(flavor_or_file)
        if not handler:
            raise AttributeError(f"Cannot find model flavor '{flavor_or_file}'. Legal values are: {set(_model_handlers.keys())}.")
        return handler
