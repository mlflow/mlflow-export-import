
import os
import tempfile
from mlflow_export_import.common import mlflow_utils, io_utils
from mlflow_export_import.common.find_artifacts import find_run_model_names

def get_model_name(artifact_path):
    idx = artifact_path.find("artifacts/")
    idx += len("artifacts/")
    return artifact_path[idx:]


def update_mlmodel_run_id(mlflow_client, run_id):
    """
    :param: mlflow_client
    :param: run_id
    Workaround to fix the run_id in the destination MLmodel file since there is no method to get all model artifacts of a run.
    Since an MLflow run does not keep track of its models, there is no method to retrieve the artifact path to all its models.
    This workaround recursively searches the run's root artifact directory for all MLmodel files, and assumes their directory
    represents a path to the model.
    """
    mlmodel_paths = find_run_model_names(mlflow_client, run_id)
    for model_path in mlmodel_paths:
        download_uri = f"runs:/{run_id}/{model_path}/MLmodel"
        local_path = mlflow_utils.download_artifacts(mlflow_client, download_uri)
        mlmodel = io_utils.read_file(local_path, "yaml")
        mlmodel["run_id"] = run_id
        with tempfile.TemporaryDirectory() as dir:
            output_path = os.path.join(dir, "MLmodel")
            io_utils.write_file(output_path, mlmodel, "yaml")
            if model_path == "MLmodel":
                model_path = ""
            mlflow_client.log_artifact(run_id, output_path, model_path)
