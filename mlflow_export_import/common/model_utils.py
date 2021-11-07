import time
from mlflow.exceptions import RestException
from mlflow.entities.model_registry.model_version_status import ModelVersionStatus

def delete_model(client, model_name, sleep_time=5):
    """ Delete a model and all its versions. """
    try:
        versions = client.get_latest_versions(model_name)
        print(f"Deleting model '{model_name}' and {len(versions)} versions")
        for v in versions:
            print(f"  version={v.version} status={v.status} stage={v.current_stage} run_id={v.run_id}")
            client.transition_model_version_stage (model_name, v.version, "Archived")
            time.sleep(sleep_time) # Wait until stage transition takes hold
            client.delete_model_version(model_name, v.version)
        client.delete_registered_model(model_name)
    except RestException:
        pass

def wait_until_version_is_ready(client, model_name, model_version, sleep_time=1, iterations=100):
    """ Due to blob eventual consistency, wait until a newly created version is in READY state. """
    start = time.time()
    for _ in range(iterations):
        version = client.get_model_version(model_name, model_version.version)
        status = ModelVersionStatus.from_string(version.status)
        _show_version(version)
        if status == ModelVersionStatus.READY:
            break
        time.sleep(sleep_time)
    end = time.time()
    print(f"Waited {round(end-start,2)} seconds")

def _show_version(version):
    print(f"Version: id={version.version} status={version.status} state={version.current_stage}")

def dump_model_versions(client, model_name):
    import pandas as pd
    from tabulate import tabulate
    versions = client.get_latest_versions(model_name)
    versions = [ [vr.version, vr.current_stage] for vr in versions ]
    df = pd.DataFrame(versions, columns = ["Version","Stage"])
    print(f"\nLatest {len(versions)} versions")
    print(tabulate(df, headers="keys", tablefmt="psql", showindex=False))

    versions = client.search_model_versions(f"name='{model_name}'")
    versions = sorted(versions, key=lambda x: x.current_stage)
    versions = [ [vr.version, vr.current_stage, vr.status] for vr in versions ]
    df = pd.DataFrame(versions, columns = ["Version","Stage", "Status"])
    print(f"\nSearch {len(versions)} versions:")
    print(tabulate(df, headers="keys", tablefmt="psql", showindex=False))
