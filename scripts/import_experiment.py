import os
from dotenv import load_dotenv
from mlflow_export_import.client import client_utils
from mlflow_export_import.common import mlflow_utils
from mlflow_export_import.experiment.import_experiment import import_experiment

load_dotenv()

mlflow_tracking_uri = os.getenv("MLFLOW_TRACKING_URI_IMPORT")

print(mlflow_tracking_uri)

experiment_id_or_name="register_model_with_component"
input_dir="output/b1820082-3b5a-4532-a20d-4942af079ae8"

import_experiment(
    experiment_name=experiment_id_or_name,
    input_dir=input_dir,
    import_source_tags = False,
    import_permissions = False,
    use_src_user_id = False,
    dst_notebook_dir = None,
    mlflow_tracking_uri=mlflow_tracking_uri
)