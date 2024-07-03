import click

def opt_input_file(function):
    function = click.option("--input-file",
        help="Input file.",
        type=str,
        required=True
    )(function)
    return function

def opt_output_file(function):
    function = click.option("--output-file",
        help="Output file.",
        type=str,
        required=False
    )(function)
    return function

def opt_model_uri(function):
    function = click.option("--model-uri",
        help="Model URI such as 'models:/my_model/3' or 'runs:/73ab168e5775409fa3595157a415bb62/my_model'.",
        type=str,
        required=True
    )(function)
    return function

def opt_filter(function):
    function = click.option("--filter",
        help="For OSS MLflow this is a filter for search_model_versions(), for Databricks it is for search_registered_models() due to Databricks MLflow search limitations.",
        type=str,
        required=False
    )(function)
    return function

def opt_use_get_model_info(function):
    function = click.option("--use-get-model-info",
        help="Use mlflow.models.get_model_info() which apparently downloads *all* artifacts (quite slow for large models) instead of just downloading 'MLmodel' using mlflow.artifacts.download_artifacts().",
        type=bool,
        default=False,
        show_default=True
    )(function)
    return function
