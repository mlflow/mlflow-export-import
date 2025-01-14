import os
from dotenv import load_dotenv
from mlflow_export_import.client import client_utils
from mlflow_export_import.common import mlflow_utils
from mlflow_export_import.experiment.export_experiment import export_experiment

load_dotenv()

mlflow_tracking_uri = os.getenv("MLFLOW_TRACKING_URI")

print(mlflow_tracking_uri)

experiment_id_or_name="inference-feature-selection"
output_dir="output"

mlflow_client = client_utils.create_mlflow_client_from_tracking_uri(mlflow_tracking_uri)
experiment = mlflow_utils.get_experiment(mlflow_client, experiment_id_or_name)
output_dir = f"{output_dir}/{experiment.experiment_id}"

run_start_date=None
export_permissions=None
notebook_formats=None

print("experiment_id:", experiment.experiment_id)
print("experiment_name:", experiment.name)       
print("output_dir:", output_dir)

export_experiment(
    experiment_id_or_name = experiment.experiment_id,
    output_dir = output_dir,
    run_start_time = run_start_date,
    export_permissions = export_permissions,
    notebook_formats = notebook_formats
)