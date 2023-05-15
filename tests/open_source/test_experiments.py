from mlflow.entities import ViewType
from mlflow_export_import.experiment.export_experiment import export_experiment
from mlflow_export_import.experiment.import_experiment import import_experiment
from tests.open_source.oss_utils_test import create_simple_run, init_output_dirs, mk_dst_experiment_name
from tests.open_source.oss_utils_test import _create_simple_run
from tests.open_source.oss_utils_test import create_test_experiment
from tests.compare_utils import compare_runs, compare_experiment_tags
from tests.open_source.init_tests import mlflow_context

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

    dst_exp_name = mk_dst_experiment_name(exp1.name)

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


# == basic tests

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

# == Test export/import deleted runs

def test_export_deleted_runs(mlflow_context):
    init_output_dirs(mlflow_context.output_dir)
    exp1 = create_test_experiment(mlflow_context.client_src, 3)

    runs1 =  mlflow_context.client_src.search_runs(exp1.experiment_id)
    assert len(runs1) == 3

    mlflow_context.client_src.delete_run(runs1[0].info.run_id)
    runs1 =  mlflow_context.client_src.search_runs(exp1.experiment_id)
    assert len(runs1) == 2

    runs1 =  mlflow_context.client_src.search_runs(exp1.experiment_id, run_view_type=ViewType.ALL)
    assert len(runs1) == 3

    export_experiment(
        mlflow_client = mlflow_context.client_src,
        experiment_id_or_name = exp1.name,
        output_dir = mlflow_context.output_dir,
        export_deleted_runs = True
    )

    dst_exp_name = mk_dst_experiment_name(exp1.name)
    import_experiment(
        mlflow_client = mlflow_context.client_dst,
        experiment_name = dst_exp_name,
        input_dir = mlflow_context.output_dir
    )
    exp2 = mlflow_context.client_dst.get_experiment_by_name(dst_exp_name)
    runs2 =  mlflow_context.client_dst.search_runs(exp2.experiment_id)
    assert len(runs2) == 2
    runs2 =  mlflow_context.client_dst.search_runs(exp2.experiment_id, run_view_type=ViewType.ALL)
    assert len(runs2) == 3


# == Test start_date filter 

def test_filter_run_no_start_date(mlflow_context):
    _run_test_run_start_date(mlflow_context, 0)

def test_filter_run_start_date_after(mlflow_context):
    _run_test_run_start_date(mlflow_context, 2)

def test_filter_run_start_date_before(mlflow_context):
    _run_test_run_start_date(mlflow_context, -2)


def _run_test_run_start_date(mlflow_context, sleep_time):
    init_output_dirs(mlflow_context.output_dir)
    exp1, run1a = create_simple_run(mlflow_context.client_src)
    run1a = mlflow_context.client_src.get_run(run1a.info.run_id)

    if sleep_time == 0:
        run_start_time = None
    elif sleep_time > 0:
        time.sleep(sleep_time)
        run_start_time = _fmt_utc_time_now()
        time.sleep(sleep_time)
    else:
        run_start_time = _fmt_utc_time_before(abs(sleep_time))

    _create_simple_run(mlflow_context.client_src)

    export_experiment(
        mlflow_client = mlflow_context.client_src,
        experiment_id_or_name = exp1.name,
        output_dir = mlflow_context.output_dir,
        run_start_time = run_start_time
    )

    dst_exp_name = mk_dst_experiment_name(exp1.name)

    import_experiment(
        mlflow_client = mlflow_context.client_dst,
        experiment_name = dst_exp_name,
        input_dir = mlflow_context.output_dir
    )

    exp2 = mlflow_context.client_dst.get_experiment_by_name(dst_exp_name)
    runs2 = mlflow_context.client_dst.search_runs(exp2.experiment_id)
    if sleep_time == 0:
        assert 2 == len(runs2)
    elif sleep_time > 0:
        assert 1 == len(runs2)
    else:
        assert 2 == len(runs2)


from mlflow_export_import.common.timestamp_utils import TS_FORMAT
from datetime import datetime
import time

def _fmt_utc_time_before(seconds_before):
    seconds = time.time() - seconds_before
    dt = datetime.utcfromtimestamp(seconds)
    return dt.strftime(TS_FORMAT)

def _fmt_utc_time_now():
    from datetime import timezone
    return datetime.now(timezone.utc).strftime(TS_FORMAT)
