""" 
Lists all registered models.
"""

import json
from mlflow_export_import.client.http_client import MlflowHttpClient

def main():
    client = MlflowHttpClient()
    print("HTTP client:",client)
    rsp = client._get("registered-models/search")
    dct = json.loads(rsp.text)
    print(json.dumps(dct,indent=2)+"\n")

if __name__ == "__main__":
    main()
