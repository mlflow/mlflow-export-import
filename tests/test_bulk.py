import os
import mlflow
from utils_test import create_output_dir, create_experiment, output_dir, mk_uuid
from sklearn_utils import create_sklearn_model
from compare_utils import compare_runs, compare_run_no_import_mlflow_tags

from mlflow_export_import.bulk.export_experiments import export_experiments
from mlflow_export_import.bulk.import_experiments import import_experiments

notebook_formats = "SOURCE,DBC"

# == Setup

client = mlflow.tracking.MlflowClient()
mlmodel_fix = True

def _create_simple_run(idx):
    model = create_sklearn_model(max_depth=4)
    with mlflow.start_run(run_name=f"run_{idx}"):
        mlflow.log_param("run_index",idx)
        mlflow.log_metric("rmse",.789+idx)
        mlflow.set_tag("my_uuid",mk_uuid())
        mlflow.set_tag("run_index",idx)
        mlflow.sklearn.log_model(model, "model")
        with open("info.txt", "w") as f:
            f.write("Hi artifact")
        mlflow.log_artifact("info.txt")
        mlflow.log_artifact("info.txt","dir2")
        mlflow.log_metric("m1", idx)

def _create_test_experiment(num_runs):
    exp = create_experiment()
    for j in range(num_runs):
        _create_simple_run(j)
    return exp

# == Export/import Experiments tests

def _run_test(compare_func, import_mlflow_tags=True, export_metadata_tags=False, use_threads=False):
    create_output_dir()
    exp1 = _create_test_experiment(3)
    experiments = exp1.name
    export_experiments(experiments=experiments,
        output_dir=output_dir,
        export_metadata_tags=export_metadata_tags,
        notebook_formats=notebook_formats,
        use_threads=use_threads)

    exp_prefix = "Imported_"
    import_experiments(output_dir, experiment_name_prefix=exp_prefix, use_src_user_id=False, import_mlflow_tags=import_mlflow_tags, import_metadata_tags=False, use_threads=False)

    base_dir = os.path.join(output_dir,"compare_runs")
    os.makedirs(base_dir)
    exp2 = client.get_experiment_by_name(exp_prefix + exp1.name)
    for run1 in client.search_runs(exp1.experiment_id, ""):
        tag = run1.data.tags["run_index"]
        run2 = client.search_runs(exp2.experiment_id, f"tags.run_index = '{tag}'")[0]
        odir = os.path.join(base_dir,run1.info.experiment_id)
        compare_func(client, odir, run1, run2)

def test_exp_basic():
    _run_test(compare_runs, import_mlflow_tags=False)

def test_exp_basic_threads():
    _run_test(compare_runs, import_mlflow_tags=False, use_threads=True)

def test_exp_no_import_mlflow_tags():
    _run_test(compare_run_no_import_mlflow_tags, import_mlflow_tags=False)

def test_exp_import_metadata_tags():
    _run_test(compare_run_no_import_mlflow_tags, export_metadata_tags=True)
