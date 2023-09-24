from typing import Any
from dataclasses import dataclass


@dataclass()
class MlflowContext:
    """ 
    For tests.open_source tests. Original tests.
    """ 
    client_src: Any
    client_dst: Any
    output_dir: str
    output_run_dir: str


@dataclass()
class TestContext:
    """ 
    For tests.databricks tests. Newer tests.
    """ 
    mlflow_client_src: Any
    mlflow_client_dst: Any
    dbx_client_src: Any
    dbx_client_dst: Any
    output_dir: str
    output_run_dir: str


def to_MlflowContext(test_context):
    """
    Convert TestContext to MlflowContext in order to reuse plentiful existing test comparisons.
    """
    return MlflowContext(
        test_context.mlflow_client_src,
        test_context.mlflow_client_dst,
        test_context.output_dir,
        test_context.output_run_dir
    )
