from init_tests import test_context
from databricks_cli.dbfs.api import DbfsPath


def test_run(test_context):
    _bounce_dbfs_dir(test_context, test_context.tester.dst_run_base_dir)
    test_context.tester.run_job(test_context.tester.run_export_run_job, "Export Run")
    _check_dbfs_dir_after_export(test_context, test_context.tester.dst_run_base_dir)


def test_export_experiment_job(test_context):
    _bounce_dbfs_dir(test_context, test_context.tester.dst_exp_base_dir)
    test_context.tester.run_job(test_context.tester.run_export_experiment_job, "Export Experiment")
    _check_dbfs_dir_after_export(test_context, test_context.tester.dst_exp_base_dir)


def test_export_model(test_context):
    _bounce_dbfs_dir(test_context, test_context.tester.dst_model_base_dir)
    test_context.tester.run_job(test_context.tester.run_export_model_job, "Export Model")
    _check_dbfs_dir_after_export(test_context, test_context.tester.dst_exp_base_dir)


def _bounce_dbfs_dir(test_context, dir):
    """ Delete the export directory and recreate it """
    dir = DbfsPath(dir)
    test_context.dbfs_api.delete(dir, True)
    test_context.dbfs_api.mkdirs(dir)
    files = test_context.dbfs_api.list_files(dir)
    assert len(files) == 0


def _check_dbfs_dir_after_export(test_context, dir):
    """ Minimal check to see if we have created the MLflow object's export directory. More checks needed. """
    files = test_context.dbfs_api.list_files(DbfsPath(dir))
    assert len(files) > 0
    sub_dir = files[0]
    files = test_context.dbfs_api.list_files(sub_dir.dbfs_path)
    assert len(files) > 0
