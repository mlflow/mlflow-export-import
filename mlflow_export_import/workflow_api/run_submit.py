import sys
import click
import logging
from mlflow_export_import.workflow_api.workflow_api_client import WorkflowApiClient
from mlflow_export_import.workflow_api import utils

def run(profile,spec_file, sleep_seconds, timeout_seconds, verbose=False):
    client = WorkflowApiClient(profile, sleep_seconds, timeout_seconds)

    # Read JSON spec file
    job_spec = utils.load_json_file(spec_file)

    # Launch run jobs/submit
    res = client.run_submit(job_spec)

    run_id = res["run_id"]
    logging.info(f"New run_id: {run_id}")

    # Wait until cluster is created
    client.wait_until_cluster_is_created_for_run(run_id)

    # Get cluster ID
    dct = client.get_run(run_id)
    #cluster_state = dct["cluster_instance"]["cluster_id"]
    cluster_id = dct["cluster_instance"]["cluster_id"]
    logging.info(f"cluster_id: {cluster_id}")

    # Wait until run is done
    client.wait_until_run_is_done(run_id)

    # Get run status
    run = client.get_run(run_id)

    # Show final run 
    if verbose:
        utils.dump_as_json("Final run", run)

    # Get cluster log directory
    try:
        log_dir = run["cluster_spec"]["new_cluster"]["cluster_log_conf"]["dbfs"]["destination"] + "/" + cluster_id
        logging.info(f"Log directory: '{log_dir}'")
    except KeyError:
        logging.warning(f"No cluster log directory")

    # Show run result state
    result_state = run["state"]["result_state"]
    logging.info(f"Run result state: {result_state}")



@click.command()
@click.option("--profile",
    help="Databricks profile",
    type=str,
    default=None,
    show_default=True
)
@click.option("--spec-file",
    help="JSON job specification file",
    type=str,
    required=True,
    show_default=True
)
@click.option("--sleep-seconds",
    help="Sleep time for checking run status(seconds)",
    type=int,
    default=5,
    show_default=True
)
@click.option("--timeout-seconds",
    help="Timeout (seconds)",
    type=int,
    default=sys.maxsize,
    show_default=True
)
@click.option("--verbose", 
    help="Verbose", 
    type=bool, 
    default=False)

def main(profile, spec_file, sleep_seconds, timeout_seconds, verbose):
    print("Options:")
    for k,v in locals().items(): print(f"  {k}: {v}")
    run(profile, spec_file, sleep_seconds, timeout_seconds, verbose)

if __name__ == "__main__":
    main()
