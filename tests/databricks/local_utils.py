import mlflow
from tests.open_source.oss_utils_test import mk_test_object_name_default
from tests.open_source import sklearn_utils
from . init_tests import workspace_src


def to_MlflowContext(test_context):
    """
    Convert TestContext to tests.open_source MlflowContext in order to reuse test comparisons.
    """
    from tests.open_source.init_tests import MlflowContext
    return MlflowContext(
        test_context.mlflow_client_src,
        test_context.mlflow_client_dst,
        test_context.output_dir,
        test_context.output_run_dir
    )


def mk_experiment_name(workspace=workspace_src):
    return f"{workspace.base_dir}/{mk_test_object_name_default()}"


def create_experiment(client):
    exp_id = client.create_experiment(mk_experiment_name(), tags={"ocean": "southern"})
    return client.get_experiment(exp_id)


def create_run(client, experiment_id):
    max_depth = 4
    model = sklearn_utils.create_sklearn_model(max_depth)
    ori_tracking_uri = mlflow.tracking.get_tracking_uri()
    mlflow.set_tracking_uri(client.tracking_uri)
    with mlflow.start_run(experiment_id=experiment_id) as run:
        mlflow.log_param("max_depth",max_depth)
        mlflow.log_metric("rmse", 0.789)
        mlflow.set_tag("my_tag", "my_val")
        mlflow.sklearn.log_model(model, "model")
        mlflow.set_tag("south_america", "aconcagua")
        with open("info.txt", "w", encoding="utf-8") as f:
            f.write("Hi artifact")
        mlflow.log_artifact("info.txt")
    mlflow.set_tracking_uri(ori_tracking_uri)
    return client.get_run(run.info.run_id)


def create_version(client, model_name, stage=None, archive_existing_versions=False):
    exp_src = create_experiment(client)
    run = create_run(client, exp_src.experiment_id)
    source = f"{run.info.artifact_uri}/model"
    desc = "My model desc"
    tags = { "city": "yaxchilan" }
    model = client.create_registered_model(model_name, tags, desc)
    vr = client.create_model_version(model_name, source, run.info.run_id, description=desc, tags=tags)
    if stage:
        vr = client.transition_model_version_stage(model_name, vr.version, stage, archive_existing_versions)
    return vr, model
