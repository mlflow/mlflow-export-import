import click

# == Export model version

def opt_version(function):
    function = click.option("--version",
        help="Registered model version.",
        type=str,
        required=True)(function)
    return function

