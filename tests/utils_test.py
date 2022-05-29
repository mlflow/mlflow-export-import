import os
import shutil
import shortuuid
import mlflow
import mlflow.sklearn
from sklearn_utils import create_sklearn_model
from mlflow_export_import.common import model_utils

print("Mlflow path:", mlflow.__file__)
print("MLflow version:", mlflow.__version__)

#client = mlflow.tracking.MlflowClient()
#output_dir = "out"

def create_output_dir(output_dir):
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)

def init_output_dirs(output_dir):
    create_output_dir(output_dir)
    os.makedirs(os.path.join(output_dir, "run1"))
    os.makedirs(os.path.join(output_dir, "run2"))

def mk_uuid():
    return shortuuid.uuid()

TEST_OBJECT_PREFIX = f"test_exim" 

def mk_test_object_name():
    return f"{TEST_OBJECT_PREFIX}_{mk_uuid()}"

def create_experiment(client):
    exp_name = f"{mk_test_object_name()}"
    mlflow.set_experiment(exp_name)
    exp = client.get_experiment_by_name(exp_name)
    for info in client.list_run_infos(exp.experiment_id):
        client.delete_run(info.run_id)
    return exp

def create_simple_run(client, use_metric_steps=False):
    exp = create_experiment(client)
    max_depth = 4
    model = create_sklearn_model(max_depth)
    with mlflow.start_run(run_name="my_run") as run:
        mlflow.log_param("max_depth",max_depth)
        if use_metric_steps:
            for j in range(0,5):
                mlflow.log_metric("rmse",.789+j,j)
        else:
            mlflow.log_metric("rmse", 0.789)
        mlflow.set_tag("my_tag", "my_val")
        mlflow.set_tag("my_uuid",mk_uuid())
        mlflow.sklearn.log_model(model, "model")
        with open("info.txt", "w") as f:
            f.write("Hi artifact")
        mlflow.log_artifact("info.txt")
        mlflow.log_artifact("info.txt", "dir2")
        mlflow.log_metric("m1", 0.1)
    return exp, run

def create_runs(client):
    create_experiment()
    with mlflow.start_run() as run:
        mlflow.log_param("p1", "hi")
        mlflow.log_metric("m1", 0.786)
        mlflow.set_tag("t1", "hi")
    return client.search_runs(run.info.experiment_id, "")

def list_experiments(client):
    return [ exp for exp in client.list_experiments() if exp.name.startswith(TEST_OBJECT_PREFIX) ]

def delete_experiment(client, exp):
    client.delete_experiment(exp.experiment_id)

def delete_experiments(client):
    for exp in client.list_experiments():
        #if exp.name.startswith(TEST_OBJECT_PREFIX):
        client.delete_experiment(exp.experiment_id)

def delete_models(client):
    for model in client.list_registered_models(max_results=1000):
        #if model.name.startswith(TEST_OBJECT_PREFIX):
        model_utils.delete_model(client, model.name)

def compare_dirs(d1, d2):
    from filecmp import dircmp
    def _compare_dirs(dcmp):
        if len(dcmp.diff_files) > 0 or len(dcmp.left_only) > 0 or len(dcmp.right_only) > 0:
            if len(dcmp.diff_files) == 1:
                if dcmp.diff_files[0] == "MLmodel": # run_id differs because we changed it to the imported run_id
                    return True
            return False
        for sub_dcmp in dcmp.subdirs.values():
            if not _compare_dirs(sub_dcmp):
                return False
        return True
    return _compare_dirs(dircmp(d1,d2))

def dump_tags(tags, msg=""):
    print(f"==== {len(tags)} Tags:",msg)
    tags = dict(sorted(tags.items()))
    for k,v in tags.items():
        print(f"  {k}: {v}")
