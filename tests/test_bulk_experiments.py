import os
import mlflow
from mlflow_export_import.bulk import bulk_utils
from utils_test import create_experiment, mk_uuid, delete_experiments
from sklearn_utils import create_sklearn_model
from compare_utils import compare_runs

from mlflow_export_import.bulk.export_experiments import export_experiments
from mlflow_export_import.bulk.import_experiments import import_experiments
from init_tests import mlflow_context

notebook_formats = "SOURCE,DBC"

# == Setup

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

def create_test_experiment(client, num_runs):
    exp = create_experiment(client)
    for j in range(num_runs):
        _create_simple_run(j)
    return exp

# == Export/import Experiments tests

def _run_test(mlflow_context, compare_func, export_metadata_tags=False, use_threads=False):
    exps = [ create_test_experiment(mlflow_context.client_src, 3), create_test_experiment(mlflow_context.client_src, 4) ]
    exp_names = [ exp.name for exp in exps ]
    export_experiments(mlflow_context.client_src,
        experiments = exp_names,
        output_dir = mlflow_context.output_dir,
        export_metadata_tags = export_metadata_tags,
        notebook_formats = notebook_formats,
        use_threads = use_threads)

    import_experiments(mlflow_context.client_dst, mlflow_context.output_dir, use_src_user_id=False, import_metadata_tags=False, use_threads=False)

    base_dir = os.path.join(mlflow_context.output_dir,"test_compare_runs")
    os.makedirs(base_dir, exist_ok=True)

    for exp1 in exps:
        exp2 = mlflow_context.client_dst.get_experiment_by_name(exp1.name)
        for run1 in mlflow_context.client_src.search_runs(exp1.experiment_id, ""):
            tag = run1.data.tags["run_index"]
            run2 = mlflow_context.client_dst.search_runs(exp2.experiment_id, f"tags.run_index = '{tag}'")[0]
            odir = os.path.join(base_dir,run1.info.experiment_id)
            compare_func(mlflow_context.client_src, odir, run1, run2)

def test_exp_basic(mlflow_context):
    _run_test(mlflow_context, compare_runs)

def test_exp_basic_threads(mlflow_context):
    _run_test(mlflow_context, compare_runs, use_threads=True)

def test_exp_import_metadata_tags(mlflow_context): 
    _run_test(mlflow_context, compare_runs, export_metadata_tags=True)

def test_get_experiment_ids_from_comma_delimited_string(mlflow_context):
    exp_ids = bulk_utils.get_experiment_ids(mlflow_context.client_src, "exp1,exp2,exp3")
    assert len(exp_ids) == 3

def test_get_experiment_ids_from_all_string(mlflow_context):
    delete_experiments(mlflow_context.client_src)
    exps = [ create_test_experiment(mlflow_context.client_src, 3), create_test_experiment(mlflow_context.client_src, 4) ]
    exp_ids = bulk_utils.get_experiment_ids(mlflow_context.client_src, "all")
    assert exp_ids == [ exp.experiment_id for exp in exps ]

def test_get_experiment_ids_from_list(mlflow_context):
    exp_ids1 = ["exp1","exp2","exp3"]
    exp_ids2 = bulk_utils.get_experiment_ids(mlflow_context.client_src, exp_ids1)
    assert exp_ids1 == exp_ids2
