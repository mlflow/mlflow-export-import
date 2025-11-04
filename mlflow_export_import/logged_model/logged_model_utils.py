
import os
import tempfile
from mlflow_export_import.common import io_utils


def update_logged_model_mlmodel_data(mlflow_client, logged_model, local_path):
    mlmodel = io_utils.read_file(local_path, "yaml")
    mlmodel["run_id"] = logged_model.source_run_id
    mlmodel["model_id"] = logged_model.model_id
    mlmodel["model_uuid"] = logged_model.model_id
    mlmodel["artifact_path"] = logged_model.artifact_location
    with tempfile.TemporaryDirectory() as tmp_dir:
        output_path = os.path.join(tmp_dir, "MLmodel")
        io_utils.write_file(output_path, mlmodel, "yaml")
        mlflow_client.log_model_artifact(logged_model.model_id, output_path)



