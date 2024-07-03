"""
List model versions without a model signature.
"""

import click
import pandas as pd
from tabulate import tabulate
import mlflow

from . click_options import opt_filter, opt_output_file, opt_use_get_model_info
from . tools_utils import search_model_versions
from . signature_utils import get_model_signature


def as_pandas_df(filter, use_get_model_info=False):
    client = mlflow.MlflowClient()
    versions = search_model_versions(client, filter)

    print(f"Found {len(versions)} model versions")
    versions_without_signatures = []
    for j, vr in enumerate(versions):
        model_uri = f"models:/{vr.name}/{vr.version}"
        if j%10 == 0:
            print(f"Processing {j}/{len(versions)}: {model_uri}")
        try:
            signature = get_model_signature(model_uri, use_get_model_info)
            if not signature:
                versions_without_signatures.append([vr.name, vr.version, vr.run_id, ""])
        except Exception as e:
            versions_without_signatures.append([vr.name, vr.version, vr.run_id, str(e)])
    #print(f"Found {len(versions)} model versions")
    print(f"Found {len(versions_without_signatures)}/{len(versions)}  model versions without signatures")

    df = pd.DataFrame(versions_without_signatures, columns = ["model","version", "run_id", "error"])
    return df.sort_values(by=["model", "version"], ascending = [True, False])


def show(filter, output_file, use_get_model_info):
    df = as_pandas_df(filter, use_get_model_info)
    print(tabulate(df, headers="keys", tablefmt="psql", numalign="right", showindex=False))
    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            df.to_csv(f, index=False)


@click.command()
@opt_filter
@opt_output_file
@opt_use_get_model_info
def main(filter, output_file, use_get_model_info):
    """
    List model versions without a model signature.
    """
    print("Options:")
    args = locals()
    for k,v in args.items():
        print(f"  {k}: {v}")
    show(filter, output_file, use_get_model_info)


if __name__ == "__main__":
    main()
