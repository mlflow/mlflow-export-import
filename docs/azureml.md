# Use the tool for Azure Machine Learning

## Development

### Prerequisites

1. Create a virtual environment and install the libraries in `requirements.txt`
2. Install the mlflow_export_import module from local repo

    ```bash
    pip install .
    ```

3. Create a `.env` file and configure the following variables:

    ```text
    MLFLOW_TRACKING_URI=<aml_mlflow_tracking_uri>
    ```

    Note: You can retrieve the MLFLOW_TRACKING_URI value from the Azure Portal, in the homepage of the AML Workspace resource.

### Run the script

#### Export experiments

1. Open the file `scripts/export_experiment.py`, update the `experiment_name` variable with your experiment name and run the script.
2. Login to Azure using the terminal and the CLI

    ```bash
    az login
    ```

3. Run the script.
