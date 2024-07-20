import click

# == export

def opt_output_dir(function):
    function = click.option("--output-dir",
        help="Output directory.", 
        type=str,
        required=True
    )(function)
    return function

def opt_notebook_formats(function):
    function = click.option("--notebook-formats",
        help="Databricks notebook formats. Values are SOURCE, HTML, JUPYTER or DBC (comma separated).",
        type=str,  
        default="", 
        show_default=True
    )(function)
    return function

def opt_run_id(function):
    function = click.option("--run-id",
        help="Run ID.",
        type=str,
        required=True
    )(function)
    return function

def opt_stages(function):
    function = click.option("--stages",
        help="Stages to export (comma separated). Default is all stages and all versions. Stages are Production, Staging, Archived and None. Mututally exclusive with option --versions.",
        type=str,
        required=False
    )(function)
    return function

def opt_export_latest_versions(function):
    function = click.option("--export-latest-versions",
        help="Export latest registered model versions instead of all versions.",
        type=bool,
        default=False,
        show_default=True
    )(function)
    return function

def opt_export_permissions(function):
    function = click.option("--export-permissions",
        help="Export Databricks permissions.",
        type=bool,
        default=False,
        show_default=True
    )(function)
    return function

def opt_get_model_version_download_uri(function):
    function = click.option("--get-model-version-download-uri",
        help="Call MLflowClient.get_model_version_download_uri() for version export.",
        type=bool,
        default=False,
        show_default=True
    )(function)
    return function

def opt_run_start_time(function):
    function = click.option("--run-start-time",
        help="Only export runs started after this UTC time (inclusive). Format: YYYY-MM-DD.",
        type=str,
        required=False
    )(function)
    return function

def opt_export_deleted_runs(function):
    function = click.option("--export-deleted-runs",
        help="Export deleted runs.",
        type=bool,
        default=False,
        show_default=True
    )(function)
    return function

def opt_export_version_model(function):
    function = click.option("--export-version-model",
        help="Export registered model version's 'cached' MLflow model.",
        type=bool,
        default=False,
        show_default=True
    )(function)
    return function

def opt_run_ids(function):
    function = click.option("--run-ids",
        help="List of run IDs to export (comma seperated).",
        type=str,
        required=False
    )(function)
    return function

def opt_check_nested_runs(function):
    function = click.option("--check-nested-runs",
        help="Check if run in the 'run-ids' option is a parent of nested runs and export all the nested runs.",
        type=bool,
        default=False,
        show_default=True
    )(function)
    return function

# == import

def opt_input_dir(function):
    function = click.option("--input-dir",
        help="Input directory.",
        type=str,
        required=True
    )(function)
    return function

def opt_import_source_tags(function):
    function = click.option("--import-source-tags",
        help="Import source information for registered model and its versions and tags in destination object.",
        type=bool,
        default=False,
        show_default=True
    )(function)
    return function

def opt_use_src_user_id(function):
    function = click.option("--use-src-user-id",
        help= """Set the destination user field to the source user field. 
                 Only valid for open source MLflow. 
                 When importing into Databricks, the source user field is ignored since it is automatically picked up from your Databricks access token. 
                 There is no MLflow API endpoint to explicity set the user_id for Run and Registered Model.""",
        type=bool,
        default=False,
        show_default=True
    )(function)
    return function

def opt_dst_notebook_dir(function):
    function = click.option("--dst-notebook-dir",
        help="Databricks destination workpsace base directory for notebook. A run ID will be added to contain the run's notebook.",
        type=str,
        required=False,
        show_default=True
    )(function)
    return function

def opt_experiment_name(function):
    function = click.option("--experiment-name",
        help="Destination experiment name.",
        type=str,
        required=True
    )(function)
    return function

def opt_experiment(function):
    function = click.option("--experiment",
        help="Experiment name or ID.",
        type=str,
        required=True
        )(function)
    return function

def opt_versions(function):
    function = click.option("--versions",
        help="Export specified versions (comma separated). Mututally exclusive with option --stages.",
        type=str,
        required=False)(function)
    return function

def opt_import_permissions(function):
    function = click.option("--import-permissions",
        help="Import Databricks permissions using the HTTP PATCH method.",
        type=bool,
        default=False,
        show_default=True)(function)
    return function


# == bulk

def opt_use_threads(function):
    click.option("--use-threads",
        help="Process in parallel using threads.",
        type=bool,
        default=False,
        show_default=True)(function)
    return function

def opt_delete_model(function):
    function = click.option("--delete-model",
        help="If the model exists, first delete the model and all its versions.",
        type=bool,
        default=False,
        show_default=True
    )(function)
    return function

def opt_experiments(function):
    function = click.option("--experiments",
        help="Experiment names or IDs (comma delimited) or filename ending with '.txt' containing them.  \
               For example, 'sklearn_wine,sklearn_iris' or '1,2'. 'all' will export all experiments. \
               Or 'experiments.txt' will contain a list of experiment names or IDs.",
        type=str,
        required=True
    )(function)
    return function

def opt_export_all_runs(function):
    function = click.option("--export-all-runs",
        help="Export all runs of experiment or just runs associated with registered model versions.",
        type=bool,
        default=False,
        show_default=True
    )(function)
    return function

def opt_experiment_rename_file(function):
    function = click.option("--experiment-rename-file",
        help="File with experiment names replacements: comma-delimited line such as 'old_name,new_name'.",
        type=str,
        required=False
    )(function)
    return function

def opt_model_rename_file(function):
    function = click.option("--model-rename-file",
        help="File with registered model names replacements: comma-delimited line such as 'old_name,new_name'.",
        type=str,
        required=False
    )(function)
    return function

# == other

def opt_model(function):
    function = click.option("--model",
        help="Registered model name.",
        type=str,
        required=True
    )(function)
    return function

def opt_verbose(function):
    function = click.option("--verbose",
        type=bool,
        help="Verbose.",
        default=False,
        show_default=True
    )(function)
    return function
