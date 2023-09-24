from mlflow_export_import.experiment.export_experiment import export_experiment
from mlflow_export_import.experiment.import_experiment import import_experiment

from tests.open_source.oss_utils_test import mk_test_object_name_default
from . init_tests import workspace_src, test_context
from . compare_utils import compare_experiments
from . import local_utils

_num_runs = 2


def test_experiment(test_context):
    exp_name = f"{workspace_src.base_dir }/{mk_test_object_name_default()}"

    client = test_context.mlflow_client_src
    exp_id = client.create_experiment(exp_name, tags={"ocean": "southern"})
    exp_src = client.get_experiment_by_name(exp_name)
    for _ in range(_num_runs):
        local_utils.create_run(client, exp_id)

    export_experiment(
        mlflow_client = test_context.mlflow_client_src,
        experiment_id_or_name = exp_name,
        output_dir = test_context.output_dir
    )
    import_experiment(
        mlflow_client = test_context.mlflow_client_dst,
        experiment_name = exp_name,
        input_dir = test_context.output_dir
    )  

    exp_dst = test_context.mlflow_client_dst.get_experiment_by_name(exp_name)
    assert exp_dst
    compare_experiments(exp_src, exp_dst, test_context.mlflow_client_src, test_context.mlflow_client_dst, _num_runs)
