import os
import mlflow

from mlflow.entities import ViewType
from mlflow_export_import.bulk import bulk_utils
from mlflow_export_import.bulk.export_experiments import export_experiments
from mlflow_export_import.bulk.import_experiments import import_experiments

import sklearn_utils
from init_tests import mlflow_context
from compare_utils import compare_runs
from oss_utils_test import (
    init_output_dirs,
    mk_uuid,
    delete_experiments_and_models,
    mk_test_object_name_default
)

_notebook_formats = "SOURCE,DBC"

# == Setup

def _create_simple_run(idx=0):
    model = sklearn_utils.create_sklearn_model(max_depth=4)
    with mlflow.start_run(run_name=f"run_{idx}"):
        mlflow.log_param("run_index", idx)
        mlflow.log_metric("rmse", 0.789+idx)
        mlflow.set_tag("my_uuid" ,mk_uuid())
        mlflow.set_tag("run_index", idx)
        mlflow.sklearn.log_model(model, "model")
        with open("info.txt", "wt", encoding="utf-8") as f:
            f.write("Hi artifact")
        mlflow.log_artifact("info.txt")
        mlflow.log_artifact("info.txt", "dir2")
        mlflow.log_metric("m1", idx)


def _create_test_experiment(client, num_runs, mk_test_object_name=mk_test_object_name_default):
    from oss_utils_test import create_experiment
    exp = create_experiment(client, mk_test_object_name)
    for j in range(num_runs):
        _create_simple_run(j)
    return exp


# == Compare

def compare_experiments(mlflow_context, compare_func):
    exps1 = sorted(_search_experiments(mlflow_context.client_src), key=lambda x: x.name)
    exps2 = sorted(_search_experiments(mlflow_context.client_dst), key=lambda x: x.name)
# ZZZ
    assert len(exps1) == len(exps2)
    for x in zip(exps1, exps2):
        exp1, exp2 = x[0], x[1]
        assert exp1.name == exp2.name
        runs1 = mlflow_context.client_src.search_runs(exp1.experiment_id)
        runs2 = mlflow_context.client_dst.search_runs(exp2.experiment_id)
        assert len(runs1) == len(runs2)
    for run1 in mlflow_context.client_src.search_runs(exp1.experiment_id, ""):
        tag = run1.data.tags["run_index"]
        run2 = mlflow_context.client_dst.search_runs(exp2.experiment_id, f"tags.run_index = '{tag}'")[0]
        #assert run1.data.tags["tags.run_index] = run2.data.tags["tags.run_index]
        base_dir = os.path.join(mlflow_context.output_dir,"test_compare_runs")
        os.makedirs(base_dir, exist_ok=True)
        odir = os.path.join(base_dir,run1.info.experiment_id)
        compare_func(mlflow_context.client_src, mlflow_context.client_dst, run1, run2, odir)

# == Export/import Experiments tests

def _run_test(mlflow_context, compare_func, use_threads=False):
    delete_experiments_and_models(mlflow_context)
    exps = [ _create_test_experiment(mlflow_context.client_src, 3), _create_test_experiment(mlflow_context.client_src, 4) ]
    exp_names = [ exp.name for exp in exps ]
    export_experiments(
        mlflow_client = mlflow_context.client_src,
        experiments = exp_names,
        output_dir = mlflow_context.output_dir,
        notebook_formats = _notebook_formats,
        use_threads = use_threads)
    import_experiments(
        mlflow_client = mlflow_context.client_dst, 
        input_dir = mlflow_context.output_dir)
    compare_experiments(mlflow_context, compare_func)


def test_exp_basic(mlflow_context):
    _run_test(mlflow_context, compare_runs)


def test_exp_basic_threads(mlflow_context):
    _run_test(mlflow_context, compare_runs, use_threads=True)


def test_get_experiment_ids_from_comma_delimited_string(mlflow_context):
    exp_ids = bulk_utils.get_experiment_ids(mlflow_context.client_src, "exp1,exp2,exp3")
    assert len(exp_ids) == 3


def test_get_experiment_ids_from_all_string(mlflow_context):
    delete_experiments_and_models(mlflow_context)
    exps = [ _create_test_experiment(mlflow_context.client_src, 3), _create_test_experiment(mlflow_context.client_src, 4) ]
    exp_ids = bulk_utils.get_experiment_ids(mlflow_context.client_src, "all")
    assert sorted(exp_ids) == sorted([exp.experiment_id for exp in exps])


def test_get_experiment_ids_from_list(mlflow_context):
    exp_ids1 = ["exp1","exp2","exp3"]
    exp_ids2 = bulk_utils.get_experiment_ids(mlflow_context.client_src, exp_ids1)
    assert exp_ids1 == exp_ids2


# == Test import with experiment replacement tests

def test_experiment_renames_do_replace(mlflow_context):
    exp = _create_test_experiment(mlflow_context.client_src, 2)
    export_experiments(
        mlflow_client = mlflow_context.client_src,
        experiments = [ exp.name ],
        output_dir = mlflow_context.output_dir)

    new_name = "foo_bar"
    import_experiments(
        mlflow_client = mlflow_context.client_dst, 
        input_dir = mlflow_context.output_dir, 
        experiment_renames = { exp.name: new_name } )

    exp2 = mlflow_context.client_dst.get_experiment_by_name(exp.name)
    assert not exp2
    exp2 = mlflow_context.client_dst.get_experiment_by_name(new_name)
    assert exp2
    assert exp2.name == new_name


def test_experiment_renames_dont_replace(mlflow_context):
    exp = _create_test_experiment(mlflow_context.client_src, 2)
    export_experiments(
        mlflow_client = mlflow_context.client_src,
        experiments = [ exp.name ],
        output_dir = mlflow_context.output_dir)

    new_name = "bar"
    import_experiments(
        mlflow_client = mlflow_context.client_dst, 
        input_dir = mlflow_context.output_dir, 
        experiment_renames = { "foo": new_name } )

    exp2 = mlflow_context.client_dst.get_experiment_by_name(exp.name)
    assert exp2
    assert exp2.name == exp.name
    exp2 = mlflow_context.client_dst.get_experiment_by_name(new_name)
    assert not exp2 

# == Test export/import deleted runs

def _purge(exps1, exps2):
    """
    Since experiment deletes are soft and not hard, we use this method to purge those
    """
    exps1 = { exp.name for exp in exps1 }
    return [ exp for exp in exps2 if exp.name not in exps1 ]

def _delete_experiments(mlflow_context):
    for exp in mlflow_context.client_src.search_experiments():
        mlflow_context.client_src.delete_experiment(exp.experiment_id)
    for exp in mlflow_context.client_dst.search_experiments():
        mlflow_context.client_dst.delete_experiment(exp.experiment_id)

def test_export_deleted_runs(mlflow_context):
    init_output_dirs(mlflow_context.output_dir)
    delete_experiments_and_models(mlflow_context)

    exp1 = _create_test_experiment(mlflow_context.client_src, 3)

    runs1 =  mlflow_context.client_src.search_runs(exp1.experiment_id)
    assert len(runs1) == 3

    mlflow_context.client_src.delete_run(runs1[0].info.run_id)
    runs1 =  mlflow_context.client_src.search_runs(exp1.experiment_id)
    assert len(runs1) == 2

    export_experiments(
        mlflow_client = mlflow_context.client_src,
        experiments = [ exp1.name ],
        output_dir = mlflow_context.output_dir,
        export_deleted_runs = True)

    import_experiments(
        mlflow_client = mlflow_context.client_dst, 
        input_dir = mlflow_context.output_dir)

    exps2 = _search_experiments(mlflow_context.client_dst)
    assert len(exps2) == 1

    exp2 = exps2[0]
    runs2 =  mlflow_context.client_dst.search_runs(exp2.experiment_id)
    assert len(runs2) == 2
    runs2 =  mlflow_context.client_dst.search_runs(exp2.experiment_id, run_view_type=ViewType.ALL)
    assert len(runs2) == 3


def _search_experiments(client):
    exps = client.search_experiments()
    return [ exp for exp in exps if exp.name != "Default" ]
