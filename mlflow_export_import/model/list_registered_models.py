""" 
Lists all registered models.
"""

import os
import json
import click
from mlflow_export_import.common.http_client import MlflowHttpClient

@click.command()
@click.option("--output-dir", help="Output directory.", default=".", type=str)
def main(output_dir):  # pragma: no cover
    print("Options:")
    for k,v in locals().items():
        print(f"  {k}: {v}")
    client = MlflowHttpClient()
    print("HTTP client:",client)
    rsp = client._get("registered-models/list")
    path = os.path.join(output_dir,"registered_models.json")
    print("Output file:",path)
    dct = json.loads(rsp.text)
    with open(path, "w") as f:
        f.write(json.dumps(dct,indent=2)+"\n")

if __name__ == "__main__":
    main()
