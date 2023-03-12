from mlflow_export_import.experiment.export_experiment import export_experiment
from mlflow_export_import.experiment.import_experiment import import_experiment
from oss_utils_test import create_simple_run, init_output_dirs, create_dst_experiment_name
from compare_utils import compare_runs, compare_experiment_tags
from init_tests import mlflow_context

# == Setup

def _init_exp_test(mlflow_context, import_source_tags=False):
    init_output_dirs(mlflow_context.output_dir)
    exp1, run1 = create_simple_run(mlflow_context.client_src)
    run1 = mlflow_context.client_src.get_run(run1.info.run_id)

    export_experiment(
        mlflow_client = mlflow_context.client_src,
        experiment_id_or_name = exp1.name,
        output_dir = mlflow_context.output_dir
    )

    dst_exp_name = create_dst_experiment_name(exp1.name)

    import_experiment(
        mlflow_client = mlflow_context.client_dst,
        experiment_name = dst_exp_name,
        input_dir = mlflow_context.output_dir,
        import_source_tags = import_source_tags
    )

    exp2 = mlflow_context.client_dst.get_experiment_by_name(dst_exp_name)
    runs = mlflow_context.client_dst.search_runs(exp2.experiment_id)
    run2 = mlflow_context.client_dst.get_run(runs[0].info.run_id)

    return exp1, exp2, run1, run2


def _compare_experiments(exp1, exp2, import_source_tags=False):
    assert exp1.name == exp2.name
    assert exp1.lifecycle_stage == exp2.lifecycle_stage
    assert exp1.artifact_location != exp2.artifact_location
    compare_experiment_tags(exp1.tags, exp2.tags, import_source_tags)


def test_exp_basic(mlflow_context):
    exp1, exp2, run1, run2 = _init_exp_test(mlflow_context)
    _compare_experiments(exp1, exp2)
    compare_runs(mlflow_context.client_src, mlflow_context.client_dst, 
        run1, run2, 
        mlflow_context.output_dir)


def test_exp_with_source_tags(mlflow_context):
    exp1, exp2, run1, run2 = _init_exp_test(mlflow_context, import_source_tags=True)
    _compare_experiments(exp1, exp2, True)
    compare_runs(mlflow_context.client_src, mlflow_context.client_dst, 
        run1, run2, 
        mlflow_context.output_dir, 
        import_source_tags=True)
