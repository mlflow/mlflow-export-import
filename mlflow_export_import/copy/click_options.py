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
        required=False
    )(function)
    return function

def opt_dst_mlflow_uri(function):
    function = click.option("--dst-mlflow-uri",
        help="Destination MLflow tracking server URI.",
        type=str,
        required=False
    )(function)
    return function

def opt_src_registry_uri(function):
    function = click.option("--src-registry-uri",
        help="Source MLflow registry URI.",
        type=str,
        required=True
    )(function)
    return function

def opt_dst_registry_uri(function):
    function = click.option("--dst-registry-uri",
        help="Destination MLflow registry URI.",
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

def opt_copy_permissions(function):
    function = click.option("--copy-permissions",
        help="Copy model permissions (only if target model does not exist).",
        type=bool,
        default=False,
        show_default=True
    )(function)
    return function

def opt_copy_stages_and_aliases(function):
    function = click.option("--copy-stages-and-aliases",
        help="Import stages and aliases.",
        type=bool,
        default=False,
        show_default=True
    )(function)
    return function

def opt_copy_lineage_tags(function):
    function = click.option("--copy-lineage-tags",
        help="Add source lineage info to destination version as tags starting with 'mlflow_exim'.",
        type=bool,
        default=False,
        show_default=True
    )(function)
    return function
