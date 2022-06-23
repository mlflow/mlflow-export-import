"""
Compare run utilities.
"""

from utils_test import compare_dirs, create_run_artifact_dirs
from mlflow_export_import.utils import strip_underscores
from mlflow_export_import.utils import TAG_PREFIX_EXPORT_IMPORT_RUN_INFO
from mlflow_export_import.utils import TAG_PREFIX_EXPORT_IMPORT_METADATA


def compare_run_with_source_tags(client_src, client_dst, output_dir, run1, run2):
    exp = client_src.get_experiment(run1.info.experiment_id)

    source_tags2 = { k:v for k,v in run2.data.tags.items() if k.startswith("mlflow_export_import.") }
    assert exp.name == source_tags2[f"{TAG_PREFIX_EXPORT_IMPORT_METADATA}.experiment_name"]

    for k,v in strip_underscores(run1.info).items():
        assert str(v) == source_tags2[f"{TAG_PREFIX_EXPORT_IMPORT_RUN_INFO}.{k}"],f"Assert failed for RunInfo field '{k}'" # NOTE: tag values must be strings

    compare_runs_no_tags(client_src, client_dst, output_dir, run1, run2)


def compare_runs_no_tags(client_src, client_dst, output_dir, run1, run2):
    run_artifact_dir1, run_artifact_dir2 = create_run_artifact_dirs(output_dir)
    assert run1.info.lifecycle_stage == run2.info.lifecycle_stage
    assert run1.info.status == run2.info.status
    _compare_data(run1, run2)
    _compare_artifacts(client_src, client_dst, run1, run2, run_artifact_dir1, run_artifact_dir2)


def compare_runs(client_src, client_dst, output_dir, run1, run2):
    compare_runs_no_tags(client_src, client_dst, output_dir, run1, run2) 


def _compare_data(run1, run2):
    assert run1.data.params == run2.data.params
    assert run1.data.metrics == run2.data.metrics

def _compare_artifacts(client_src, client_dst, run1, run2, run_artifact_dir1, run_artifact_dir2):
    path1 = client_src.download_artifacts(run1.info.run_id, ".", dst_path=run_artifact_dir1)
    path2 = client_dst.download_artifacts(run2.info.run_id, ".", dst_path=run_artifact_dir2)
    assert compare_dirs(path1, path2)


def dump_runs(run1, run2):
    from mlflow_export_import.common.dump_run import dump_run
    print("======= Run1")
    dump_run(run1)
    print("======= Run2")
    dump_run(run2)
