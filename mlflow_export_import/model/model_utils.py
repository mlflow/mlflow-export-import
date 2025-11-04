
import mlflow

def _extract_model_id(source):

    idx = source.find("models")
    if idx == 0:
        return source.split('models:/')[1]
    else:
        return source.split("models/")[1].split("/")[0]

def _get_logged_model_artifact_path(model_id, mlflow_client=None):
    mlflow_client = mlflow_client or mlflow.MlflowClient()
    return mlflow_client.get_logged_model(model_id).artifact_location
