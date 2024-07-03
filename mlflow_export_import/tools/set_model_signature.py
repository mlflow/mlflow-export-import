"""
Set the model signature of an MLflow model.

https://mlflow.org/docs/latest/python_api/mlflow.models.html#mlflow.models.set_signature
"""

import pandas as pd
import click
import mlflow
from mlflow.models.signature import infer_signature
from mlflow_export_import.common.dump_utils import dump_as_json
from . signature_utils import get_model_signature, to_json_signature


def set_signature(model_uri, input_file, output_file, overwrite_signature):
    signature = get_model_signature(model_uri)
    if signature:
        if not overwrite_signature:
            print(f"WARNING: Model '{model_uri}' already has a signature. Not overwriting signature.")
            return
        else:
            print(f"WARNING: Model '{model_uri}' already has a signature. Overwriting existing signature.")
    df_input = pd.read_csv(input_file)
    df_output = pd.read_csv(output_file)
    signature = infer_signature(df_input, df_output)
    print("New model signature:")
    dump_as_json(to_json_signature(signature.to_dict()))

    mlflow.models.set_signature(model_uri, signature)


@click.command()
@click.option("--model-uri",
  help="""
Model URI such as 'runs:/73ab168e5775409fa3595157a415bb62/my_model' or 'file:/my_mlflow_model.
Per MLflow documentation 'models:/' scheme is not supported.
""",
  type=str,
  required=True
)
@click.option("--input-file",
    help="Input CSV file with training data samples for signature.",
    type=str,
    required=True
)
@click.option("--output-file",
    help="Output CSV file with prediction data samples for signature.",
    type=str,
    required=False
)
@click.option("--overwrite-signature",
    help="Overwrite existing model signature.",
    type=bool,
    default=False,
    show_default=True
)
def main(model_uri, input_file, output_file, overwrite_signature):
    """
    Set the signature of an MLflow model.
    'models:/' scheme URIs are not accepted.
    For OSS MLflow, if you add a model signature to a run, it will automatically update any model version that was created from the run.
    """
    print("Options:")
    for k,v in locals().items():
        print(f"  {k}: {v}")
    set_signature(model_uri, input_file, output_file, overwrite_signature)

if __name__ == "__main__":
    main()
