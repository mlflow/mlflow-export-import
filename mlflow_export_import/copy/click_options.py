import click 

def opt_src_model(function):
    function = click.option("--src-model",
        help="Source registered model.",
        type=str,
        required=True
    )(function)
    return function

def opt_dst_model(function):
    function = click.option("--dst-model",
        help="Destination registered model.",
        type=str,
        required=True
    )(function)
    return function

def opt_src_version(function):
    function = click.option("--src-version",
        help="Source model version.",
        type=str,
        required=True
    )(function)
    return function

def opt_src_mlflow_uri(function):
    function = click.option("--src-mlflow-uri",
        help="Source MLflow tracking server URI.",
        type=str,
        required=True
    )(function)
    return function

def opt_dst_mlflow_uri(function):
    function = click.option("--dst-mlflow-uri",
        help="Destination MLflow tracking server URI.",
        type=str,
        required=True
    )(function)
    return function

def opt_dst_experiment_name(function):
    function = click.option("--dst-experiment-name",
        help="Destination experiment name. If specified, will copy old version's run to a new run. Else, use old version's run for new version.",
        type=str,
        required=False
    )(function)
    return function

def opt_add_copy_system_tags(function):
    function = click.option("--add-copy-system-tags",
        help="Add 'copy' system tags starting with 'mlflow_exim.'",
        type=bool,
        default=False,
        show_default=True
    )(function)
    return function
