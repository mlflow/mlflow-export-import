"""
List model versions without a model signature.
"""

import click
import pandas as pd
from tabulate import tabulate
import mlflow
from . click_options import opt_filter, opt_output_file
from . tools_utils import search_model_versions

client = mlflow.MlflowClient()

def as_pandas_df(filter):
    versions = search_model_versions(client, filter)

    print(f"Found {len(versions)} model versions")
    versions_without_signatures = []
    for j, vr in enumerate(versions):
        model_uri = f'models:/{vr.name}/{vr.version}'
        if j%10 == 0:
            print(f"{j}/{len(versions)}: {model_uri}")
        try:
            model_info = mlflow.models.get_model_info(model_uri)
            if not model_info.signature:
                versions_without_signatures.append([vr.name, vr.version, vr.run_id, ""])
        except Exception as e:
            versions_without_signatures.append([vr.name, vr.version, vr.run_id, str(e)])

    df = pd.DataFrame(versions_without_signatures, columns = ["model","version", "run_id", "error"])
    return df.sort_values(by=["model","version"], ascending = [True, False])


def show(filter, output_file):
    df = as_pandas_df(filter)
    print(tabulate(df, headers="keys", tablefmt="psql", numalign="right", showindex=False))
    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            df.to_csv(f, index=False)


@click.command()
@opt_filter
@opt_output_file
def main(filter, output_file):
    """
    List model versions without a model signature.
    """
    print("Options:")
    args = locals()
    for k,v in args.items():
        print(f"  {k}: {v}")
    show(filter, output_file)


if __name__ == "__main__":
    main()
