"""
Get the signature of an MLflow model.
"""

import click
import mlflow
from mlflow_export_import.common import io_utils
from mlflow_export_import.common.dump_utils import dump_as_json
from . click_options import opt_model_uri, opt_output_file
from . tools_utils import to_json_signature


def get(model_uri):
    model_info = mlflow.models.get_model_info(model_uri)
    if model_info.signature:
        sig =  model_info.signature.to_dict()
        return to_json_signature(sig)
    else:
        return None


@click.command()
@opt_model_uri
@opt_output_file
def main(model_uri, output_file):
    """
    Get the signature of an MLflow model.
    """
    print("Options:")
    for k,v in locals().items():
        print(f"  {k}: {v}")
    signature = get(model_uri)
    if signature:
        print("Model Signature:")
        dump_as_json(signature)
        if output_file:
            io_utils.write_file(output_file, signature)
    else:
        print(f"WARNING: No model signature for '{model_uri}'")

if __name__ == "__main__":
    main()
