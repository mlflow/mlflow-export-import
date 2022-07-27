"""
MLflow Export / Import CLI __main__ wrapper

This enables `python -m mlflow_export_import`
"""

from mlflow_export_import._cli import cli

if __name__ == "__main__":
    cli()
