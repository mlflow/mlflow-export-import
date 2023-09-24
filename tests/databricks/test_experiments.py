from mlflow_export_import.experiment.export_experiment import export_experiment
from mlflow_export_import.experiment.import_experiment import import_experiment

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
