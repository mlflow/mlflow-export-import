import os
from dotenv import load_dotenv
import mlflow
from azure.identity import AzureCliCredential
from azure.mgmt.resource import ResourceManagementClient
from azureml.core.authentication import AzureCliAuthentication
from mlflow_export_import.common import mlflow_utils
from mlflow_export_import.experiment.export_experiment import export_experiment
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Retrieve environment variables
mlflow_tracking_uri = os.getenv("MLFLOW_TRACKING_URI_EXPORT")
subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
resource_group_name = os.getenv("RESOURCE_GROUP_NAME")
workspace_name = os.getenv("AML_WORKSPACE_NAME")

# Set MLflow tracking URI
logger.debug("Setting MLflow tracking URI: %s", mlflow_tracking_uri)
mlflow.set_tracking_uri(mlflow_tracking_uri)

# Authenticate with Azure CLI
logger.debug("Acquiring Azure CLI token...")
cli_auth = AzureCliAuthentication()
credential = AzureCliCredential()
token = credential.get_token("https://management.azure.com/.default")
os.environ["AZUREML_ACCESS_TOKEN"] = token.token
os.environ["AZURE_ACCESS_TOKEN"] = token.token
logger.info("Azure CLI token acquired and set in environment.")

# Initialize Azure SDK clients
logger.debug("Initializing Azure SDK clients...")
resource_client = ResourceManagementClient(credential, subscription_id)

# Retrieve the workspace
logger.debug("Retrieving workspace '%s' in resource group '%s'...", workspace_name, resource_group_name)
workspace = resource_client.resources.get(
    resource_group_name,
    'Microsoft.MachineLearningServices',
    '',
    'workspaces',
    workspace_name,
    '2023-04-01'  # API version
)
logger.info("Workspace retrieved successfully. Workspace ID: %s", workspace.id)

# Use MLflow client
logger.debug("Setting up MLflow client...")
mlflow_client = mlflow.MlflowClient()

# Retrieve and validate experiment
experiment_id_or_name = "3eda98f8-33c9-4d04-aba8-cae579cb914d"
output_dir = f"output/{experiment_id_or_name}"
logger.debug("Retrieving experiment '%s'...", experiment_id_or_name)
experiment = mlflow_utils.get_experiment(mlflow_client, experiment_id_or_name)
logger.info("Experiment retrieved. ID: %s, Name: %s", experiment.experiment_id, experiment.name)

# Export experiment
logger.debug("Exporting experiment to '%s'...", output_dir)
export_experiment(
    experiment_id_or_name=experiment.experiment_id,
    output_dir=output_dir,
    run_start_time=None,
    export_permissions=None,
    notebook_formats=None
)
logger.info("Experiment export completed.")
