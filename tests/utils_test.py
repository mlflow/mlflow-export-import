import time
import mlflow
import mlflow.sklearn

print("Mlflow path:", mlflow.__file__)
print("MLflow version:", mlflow.__version__)

client = mlflow.tracking.MlflowClient()
exp_count = 0

def now():
    return round(time.time())

def create_experiment():
    global exp_count
    exp_name = f"test_exp_{now()}_{exp_count}"
    exp_count += 1
    mlflow.set_experiment(exp_name)
    exp = client.get_experiment_by_name(exp_name)
    for info in client.list_run_infos(exp.experiment_id):
        client.delete_run(info.run_id)
    return exp

def create_runs():
    create_experiment()
    with mlflow.start_run() as run:
        mlflow.log_param("p1", "hi")
        mlflow.log_metric("m1", 0.786)
        mlflow.set_tag("t1", "hi")
    return client.search_runs(run.info.experiment_id, "")

def delete_experiment(exp):
    client.delete_experiment(exp.experiment_id)

def compare_dirs(d1, d2):
    from filecmp import dircmp
    def _compare_dirs(dcmp):
        if len(dcmp.diff_files) > 0 or len(dcmp.left_only) > 0 or len(dcmp.right_only) > 0:
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
