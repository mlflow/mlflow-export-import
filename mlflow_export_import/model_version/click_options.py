import click


# == Export model version

def opt_version(function):
    function = click.option("--version",
        help="Registered model version.",
        type=str,
        required=True
    )(function)
    return function


def opt_vrm_export_version_model(function):
    function = click.option("--vrm-export-version-model",
        help="Export the MLflow model (from model registry) of a model version.",
        type=bool,
        default=False
    )(function)
    return function

def opt_vrm_model_artifact_path(function):
    function = click.option("--vrm-model-artifact-path",
        help="Destination artifact path of the Mlflow model of a model version.",
        type=str,
        required=False
    )(function)
    return function

def opt_skip_download_run_artifacts(function):
    function = click.option("--skip-download-run-artifacts",
        help="Skip downloading run artifacts (for fine-tuned LLM models)",
        type=bool,
        default=False
    )(function)
    return function


# == Import model version

def opt_create_model(function):
    function = click.option("--create-model",
        help="Create registered model before creating model version.",
        type=bool,
        default=False,
        show_default=True
    )(function)
    return function

def opt_experiment_name(function):
    function = click.option("--experiment-name",
        help="Destination experiment name for the version's run.",
        type=str,
        required=True
    )(function)
    return function

def opt_import_stages_and_aliases(function):
    function = click.option("--import-stages-and-aliases",
        help="Import stages and aliases.",
        type=bool,
        default=False,
        show_default=True
    )(function)
    return function

def opt_import_metadata(function):
    function = click.option("--import-metadata",
        help="Import registered model and experiment metadata (description and tags).",
        type=bool,
        default=False,
        show_default=True
    )(function)
    return function
