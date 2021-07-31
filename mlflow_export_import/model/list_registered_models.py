""" 
Lists all registered models.
"""

import os
import click
from mlflow_export_import.common.http_client import HttpClient

api_prefix = "api/2.0/mlflow"
resource = "registered-models/list"

@click.command()
@click.option("--output-dir", help="Output directory.", default=".", type=str)
def main(output_dir):  # pragma: no cover
    print("Options:")
    for k,v in locals().items():
        print(f"  {k}: {v}")
    client = HttpClient(api_prefix)
    print("HTTP client:",client)
    rsp = client._get(resource)
    path = os.path.join(output_dir,"registered_models.json")
    print("Output file:",path)
    with open(path, "w") as f:
        f.write(rsp.text)

if __name__ == "__main__":
    main()
