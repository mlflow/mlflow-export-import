from mlflow_export_import.experiment.export_experiment import export_experiment
from mlflow_export_import.experiment.import_experiment import import_experiment
from tests.utils_test import create_nested_runs
from tests.core import to_MlflowContext
from tests.compare_utils import compare_runs 

from . init_tests import test_context
from . compare_utils import compare_experiments
from . import local_utils

_num_runs = 2


def test_experiment(test_context):
    exp_src = local_utils.create_experiment(test_context.mlflow_client_src)
    for _ in range(_num_runs):
        local_utils.create_run(test_context.mlflow_client_src, exp_src.experiment_id)

    export_experiment(
        mlflow_client = test_context.mlflow_client_src,
        experiment_id_or_name = exp_src.name,
        output_dir = test_context.output_dir
    )
    import_experiment(
        mlflow_client = test_context.mlflow_client_dst,
        experiment_name = exp_src.name,
        input_dir = test_context.output_dir
    )  

    exp_dst = test_context.mlflow_client_dst.get_experiment_by_name(exp_src.name)
    assert exp_dst
    compare_experiments(exp_src, exp_dst, test_context.mlflow_client_src, test_context.mlflow_client_dst, _num_runs)


def test_nested_runs(test_context):
    client1, client2 = test_context.mlflow_client_src, test_context.mlflow_client_dst
    exp1 = local_utils.create_experiment(client1)
    exp_id1 = exp1.experiment_id
    num_levels = 3
    num_children = 2
    root1 = create_nested_runs(client1, exp_id1, num_levels, num_children)

    child_runs1 = get_child_runs(client1,  root1)
    assert len(child_runs1) == num_levels * num_children + 1
    run_ids = [ root1.info.run_id ]

    export_experiment(
        mlflow_client = client1, 
        experiment_id_or_name = exp1.name,
        run_ids = run_ids,
        check_nested_runs = True,
        output_dir = test_context.output_dir
    )
    import_experiment(
        mlflow_client = client2,
        experiment_name = exp1.name,
        input_dir = test_context.output_dir
    )  
    exp2 = client2.get_experiment_by_name(exp1.name)
    exp_id2 = exp2.experiment_id
    runs2 = client2.search_runs(exp2.experiment_id)
    assert len(runs2) == num_levels * num_children + 1

    # check root
    filter = f"tags.run_name = 'run_0'"
    runs2 = client2.search_runs(exp2.experiment_id, filter_string=filter)
    assert len(runs2) == 1
    root2 = runs2[0]
    mlflow_context = to_MlflowContext(test_context)
    compare_runs(mlflow_context, root1, root2)

    # check descendants
    for level in range(1,num_levels):
        _check_tree(mlflow_context, exp_id1, exp_id2, f"run_{level}")

def get_child_runs(client,  run):
    filter = f"tags.mlflow.rootRunId = '{run.info.run_id}'"
    return client.search_runs(run.info.experiment_id, filter_string=filter)

def _check_tree(mlflow_context, exp_id1, exp_id2, tag_level):
    ori_run_ids1, runs1 = _mk_level(mlflow_context.client_src, exp_id1, tag_level)
    ori_run_ids2, runs2 = _mk_level(mlflow_context.client_dst, exp_id2, tag_level)
    assert ori_run_ids1 == ori_run_ids2
    for run1,run2 in zip(runs1,runs2):
        compare_runs(mlflow_context, run1, run2)

def _mk_level(client, exp_id, tag_level):
    filter = f"tags.run_name = '{tag_level}'"
    runs = client.search_runs(exp_id, filter_string=filter)

    ori_run_ids = [ run.data.tags.get("ori_run_id") for run in runs ]
    ori_run_ids = sorted(set(ori_run_ids))

    runs = sorted(runs, key=lambda run: run.data.tags["ori_run_id"])
    return ori_run_ids, runs
