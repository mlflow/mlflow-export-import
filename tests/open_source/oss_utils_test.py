import time
import mlflow
from mlflow.utils.mlflow_tags import MLFLOW_RUN_NOTE # NOTE: ""mlflow.note.content" - used for Experiment Description too!

from mlflow_export_import.common import utils, model_utils
from mlflow_export_import.common.mlflow_utils import MlflowTrackingUriTweak

from tests import utils_test, sklearn_utils

_logger = utils.getLogger(__name__)

_logger.info(f"MLflow version: {mlflow.__version__}")


def init_output_dirs(output_dir):
    utils_test.create_output_dir(output_dir)
    return utils_test.create_run_artifact_dirs(output_dir)


def now():
    return round(time.time())


def mk_test_object_name_default():
    return utils_test.mk_test_object_name_default()


def mk_dst_experiment_name(experiment_name):
    # NOTE: OK as is if running two tracking servers. If running on one tracking server, will need to adjust by adding random prefix."
    return experiment_name


def mk_dst_model_name(model_name):
    return model_name


def create_experiment(client, mk_test_object_name=mk_test_object_name_default):
    exp_name = mk_test_object_name()
    mlflow.set_experiment(exp_name)
    exp = client.get_experiment_by_name(exp_name)
    client.set_experiment_tag(exp.experiment_id, "version_mlflow", mlflow.__version__)
    client.set_experiment_tag(exp.experiment_id, MLFLOW_RUN_NOTE, f"Description_{utils_test.mk_uuid()}")
    exp = client.get_experiment(exp.experiment_id)
    for info in client.search_runs(exp.experiment_id):
        client.delete_run(info.run_id)
    return exp


def create_simple_run(client, run_name=None, model_artifact="model", use_metric_steps=False):
    " Create run and create experiment "
    exp = create_experiment(client)
    run = _create_simple_run(client, run_name=run_name, model_artifact=model_artifact, use_metric_steps=use_metric_steps)
    return exp, run

def _create_simple_run(client, run_name=None, model_artifact="model", use_metric_steps=False):
    " Create run without creating experiment "
    max_depth = 4
    model = sklearn_utils.create_sklearn_model(max_depth)

    with MlflowTrackingUriTweak(client):
        with mlflow.start_run(run_name=run_name) as run:
            mlflow.log_param("max_depth",max_depth)
            if use_metric_steps:
                for j in range(5):
                    mlflow.log_metric("rmse",.789+j,j)
            else:
                mlflow.log_metric("rmse", 0.789)
            mlflow.set_tag("my_tag", "my_val")
            mlflow.set_tag("my_uuid", utils_test.mk_uuid())
            mlflow.sklearn.log_model(model, model_artifact)
            with open("info.txt", "w", encoding="utf-8") as f:
                f.write("Hi artifact")
            mlflow.log_artifact("info.txt")
            mlflow.log_artifact("info.txt", "dir2")
            mlflow.log_metric("m1", 0.1)
            mlflow.log_input(utils_test.create_iris_dataset(), context="test_training")

    return client.get_run(run.info.run_id)


def create_test_experiment(client, num_runs, mk_test_object_name=mk_test_object_name_default):
    exp = create_experiment(client, mk_test_object_name)
    for _ in range(num_runs):
        _create_simple_run(client)
    return exp


def create_version(client, model_name, stage=None, archive_existing_versions=False):
    _, run = create_simple_run(client)
    source = f"{run.info.artifact_uri}/model"
    desc = "My version desc"
    tags = { "city": "yaxchilan", "uuid": utils_test.mk_uuid() }
    vr = client.create_model_version(model_name, source, run.info.run_id, description=desc, tags=tags)
    alias = f"alias_{utils_test.mk_uuid()}"
    client.set_registered_model_alias(model_name, alias, vr.version)
    if stage:
        vr = client.transition_model_version_stage(model_name, vr.version, stage, archive_existing_versions)
    return vr, run


def list_experiments(client):
    return [ exp for exp in client.search_experiments() if exp.name.startswith(utils_test.TEST_OBJECT_PREFIX) ]


def delete_experiment(client, exp):
    client.delete_experiment(exp.experiment_id)


def delete_experiments(client):
    for exp in client.search_experiments():
        client.delete_experiment(exp.experiment_id)


def delete_models(client):
    for model in client.search_registered_models(max_results=1000):
        model_utils.delete_model(client, model.name)


def delete_experiments_and_models(mlflow_context):
    delete_experiments(mlflow_context.client_src)
    delete_experiments(mlflow_context.client_dst)
    delete_models(mlflow_context.client_src)
    delete_models(mlflow_context.client_dst)
    utils_test.create_output_dir(mlflow_context.output_dir)


def dump_tags(tags, msg=""):
    print(f"==== {len(tags)} Tags:",msg)
    tags = dict(sorted(tags.items()))
    for k,v in tags.items():
        print(f"  {k}: {v}")


# == Simple create experiment

_exp_count = 0

def create_simple_experiment(client):
    global _exp_count
    exp_name = f"test_exp_{now()}_{_exp_count}"
    _exp_count += 1
    mlflow.set_experiment(exp_name)
    exp = client.get_experiment_by_name(exp_name)
    for run in client.search_runs(exp.experiment_id):
        client.delete_run(run.info.run_id)
    return exp
