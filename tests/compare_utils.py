import os
from utils_test import compare_dirs
#from utils_test import dump_tags
from mlflow_export_import.common.dump_run import dump_run

# == Compare runs

def compare_run_with_metadata_tags(client, output_dir, run1, run2):
    compare_runs_no_tags(client, output_dir, run1, run2)
    exp = client.get_experiment(run1.info.experiment_id)
    metadata_tags2 = { k:v for k,v in run2.data.tags.items() if k.startswith("mlflow_export_import.metadata") }
    assert run1.info.experiment_id == metadata_tags2["mlflow_export_import.metadata.experiment_id"]
    assert exp.name == metadata_tags2["mlflow_export_import.metadata.experiment_name"]
    assert run1.info.run_id == metadata_tags2["mlflow_export_import.metadata.run_id"]
    assert run1.info.user_id == metadata_tags2["mlflow_export_import.metadata.user_id"]
    assert run1.info.artifact_uri == metadata_tags2["mlflow_export_import.metadata.artifact_uri"]
    assert run1.info.status == metadata_tags2["mlflow_export_import.metadata.status"]
    assert run1.info.start_time == int(metadata_tags2["mlflow_export_import.metadata.start_time"])
    assert run1.info.end_time == int(metadata_tags2["mlflow_export_import.metadata.end_time"])

def compare_runs_no_tags(client, output_dir, run1, run2):
    assert run1.info.lifecycle_stage == run2.info.lifecycle_stage
    assert run1.info.status == run2.info.status
    assert run1.data.params == run2.data.params
    assert run1.data.metrics == run2.data.metrics
    #dump_runs(run1, run2)
    os.makedirs(os.path.join(output_dir,"run1"), exist_ok=True) 
    os.makedirs(os.path.join(output_dir,"run2"), exist_ok=True)
    path1 = client.download_artifacts(run1.info.run_id, ".", dst_path=os.path.join(output_dir,"run1"))
    path2 = client.download_artifacts(run2.info.run_id, ".", dst_path=os.path.join(output_dir,"run2"))
    assert compare_dirs(path1, path2)

def compare_runs(client, output_dir, run1, run2):
    compare_runs_no_tags(client, output_dir, run1, run2) 

def dump_runs(run1, run2):
    print("======= Run1")
    dump_run(run1)
    print("======= Run2")
    dump_run(run2)
