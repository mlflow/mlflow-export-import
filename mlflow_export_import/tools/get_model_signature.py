"""
Get the signature of an MLflow model.
"""

import click
from mlflow_export_import.common import io_utils
from mlflow_export_import.common.dump_utils import dump_as_json
from . click_options import opt_model_uri, opt_output_file, opt_use_get_model_info
from . signature_utils import get_model_signature


@click.command()
@opt_model_uri
@opt_output_file
@opt_use_get_model_info
def main(model_uri, output_file, use_get_model_info):
    """
    Get the signature of an MLflow model.
    """
    print("Options:")
    for k,v in locals().items():
        print(f"  {k}: {v}")
    signature = get_model_signature(model_uri, use_get_model_info)
    if signature:
        print("Model Signature:")
        dump_as_json(signature)
        if output_file:
            io_utils.write_file(output_file, signature)
    else:
        print(f"WARNING: No model signature for '{model_uri}'")

if __name__ == "__main__":
    main()
