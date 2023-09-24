import mlflow
import sklearn_utils


class Dict2Class():
    def __init__(self, dct):
        self.dct = dct
        for k,v in dct.items():
            if isinstance(v,dict):
                v = Dict2Class(v)
            setattr(self, k, v)
    def __str__(self):
        return str(self.dct)


def create_run(mlflow_client, experiment_id):
    max_depth = 4
    run = mlflow_client.create_run(experiment_id)
    model = sklearn_utils.create_sklearn_model(max_depth)

    path = "out/model.pkl"
    _write_model(model, path)
    mlflow_client.log_artifact(run.info.run_id, path, "model")

    mlflow_client.log_param(run.info.run_id, "max_depth",max_depth)
    mlflow_client.set_terminated(run.info.run_id)
    return run.info.run_id

def _write_model(model, path):
    import cloudpickle as pickle
    with open(path,"wb") as f:
        pickle.dump(model, f)


def _create_run(mlflow_client, experiment_id):
    max_depth = 4

    ori_tracking_uri = mlflow.tracking.get_tracking_uri()
    mlflow.set_tracking_uri(mlflow_client.tracking_uri)

    run = mlflow_client.create_run(experiment_id)
    model = sklearn_utils.create_sklearn_model(max_depth)
    mlflow_client.log_param(run.info.run_id, "max_depth",max_depth)
    mlflow_client.log_metric("auc", .789)
    mlflow_client.set_tag("south_america", "aconcagua")
    mlflow_client.set_tag("north_america", "denali")
    mlflow.sklearn.log_model(model,"model")

    mlflow.set_tracking_uri(ori_tracking_uri)

    mlflow_client.set_terminated(run.info.run_id)
    return run.info.run_id
