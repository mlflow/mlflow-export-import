import os
import json
import mlflow
from databricks_cli.sdk import service

from mlflow_export_import.common import mlflow_utils
from mlflow_export_import.workflow_api.workflow_api_client import WorkflowApiClient
import utils

workflow_client = WorkflowApiClient()
mlflow_client = mlflow.tracking.MlflowClient()

from databricks_cli.workspace.api import WorkspaceApi
from databricks_cli.dbfs.api import DbfsApi, DbfsPath
from databricks_cli.clusters.api import ClusterApi
    
_formats = [ "SOURCE" ]
_export_src_tags = "yes"

_experiment_nb = "Iris_Train"
_experiment_name = "Iris_Train_exp"

_fs_nb_base_dir = "../../databricks_notebooks/git"
_fs_experiment_nb_name = "Iris_Train.py" 
_fs_experiment_nb_path = os.path.join("experiment", _fs_experiment_nb_name)
print("_fs_experiment_nb_path:",_fs_experiment_nb_path)


class DatabricksTester():
    def __init__(self, ws_base_dir, dst_base_dir, cluster_spec, model_name, run_name_prefix, profile=None, verbose=False):
        api_client = utils.get_api_client(profile)
        self.ws_api = WorkspaceApi(api_client)
        self.dbfs_api = DbfsApi(api_client)
        self.cluster_api = ClusterApi(api_client)
        self.jobs_service = service.JobsService(api_client)

        self.ws_base_dir = ws_base_dir
        self.dst_base_dir = dst_base_dir
        self.dst_run_base_dir = os.path.join(dst_base_dir, "runs")
        self.dst_exp_base_dir = os.path.join(dst_base_dir, "experiments")
        self.dst_model_base_dir = os.path.join(dst_base_dir, "models")

        self.model_name = model_name
        self.run_name_prefix = run_name_prefix
        self.verbose = verbose
        self.cluster_spec = cluster_spec
        self.cluster_id = self._get_cluster_id()

        self.ml_nb_path = self._mk_ws_path(_experiment_nb)
        self.ml_exp_path = self._mk_ws_path(_experiment_name)
        print("ML training notebook:", self.ml_nb_path)
        print("ML training experiment:", self.ml_exp_path)

        self.delete_experiments(mlflow_client, self.ws_base_dir)
        self._init_dirs()


    def _init_dirs(self):
        """
        Create/cleanup workspace and DBFS test directories.
        Copy notebooks to workspace test directory.
        """
        self._ws_mkdir(self.ws_base_dir)
        self._ws_list(self.ws_base_dir)
        self._import_notebook(_fs_experiment_nb_name, "experiment", self.ws_base_dir) # import the model training notebook
        self._import_notebooks(_fs_nb_base_dir, self.ws_base_dir) # import all the export-import notebooks
        self.dbfs_api.mkdirs(DbfsPath(self.dst_base_dir))


    def _get_cluster_id(self):
        if isinstance(self.cluster_spec, str):
            return self.cluster_spec
        elif isinstance(self.cluster_spec, dict):
            res = self.cluster_api.create_cluster(self.cluster_spec)
            return res["cluster_id"]
        raise Exception("Unknown cluster type")


    def delete_cluster(self):
        if isinstance(self.cluster_spec, dict):
            self.cluster_api.permanent_delete(self.cluster_id)


    def _run_job(self, nb_name, notebook_task):
        run_name = self._mk_run_name(nb_name)
        if self.verbose:
            self._dump_json(f"Run job {run_name} - notebook_task", notebook_task)
        return self.jobs_service.submit_run(run_name, existing_cluster_id=self.cluster_id, notebook_task=notebook_task)


    def run_export_run_job(self):
        run = mlflow_utils.get_first_run(mlflow_client, self.ml_exp_path)
        nb_name = "Export_Run"
        nb_path = self._mk_ws_path(nb_name)
        notebook_task = {
            "notebook_path": nb_path,
            "base_parameters": {
              " Run ID": run.info.run_id,
              "Destination base folder": self.dst_run_base_dir,
              "Export source tags": _export_src_tags
            }
        }
        return self._run_job(nb_name, notebook_task)


    def run_export_experiment_job(self):
        nb_name = "Export_Experiment"
        nb_path = self._mk_ws_path(nb_name)
        notebook_task = { 
            "notebook_path": nb_path,
            "base_parameters": {
              " Experiment ID or Name": self.ml_exp_path,
              "Destination base folder": self.dst_exp_base_dir,
              "Export source tags": _export_src_tags,
              "Registered model": self.model_name
            }
        }
        return self._run_job(nb_name, notebook_task)


    def run_export_model_job(self):
        nb_name = "Export_Model"
        nb_path = self._mk_ws_path(nb_name)
        notebook_task = { 
            "notebook_path": nb_path,
            "base_parameters": {
              " Model": self.model_name,
              "Destination base folder": self.dst_model_base_dir,
              "Export source tags": _export_src_tags,
            }
        }
        return self._run_job(nb_name, notebook_task)


    def run_training_job(self):
        run_name = self._mk_run_name("training_job")
        notebook_task = { 
            "notebook_path": self.ml_nb_path,
            "base_parameters": {
              "Experiment": self.ml_exp_path,
              "Registered model": self.model_name
            }
        }
        if self.verbose:
            self._dump_json("run_training_job - notebook_task",notebook_task)
        return self.jobs_service.submit_run(run_name, existing_cluster_id=self.cluster_id, notebook_task=notebook_task)


    def run_import_experiment_job(self):
        nb_name = "Import_Experiment"
        exp = mlflow_client.get_experiment_by_name(self.ml_exp_path)
        assert exp
        dst_exp_name = self._mk_imported_exp_name()
        src_exp_dir = self._mk_dbfs_path(exp.experiment_id)
        notebook_task = {
            "notebook_path": self._mk_ws_path(nb_name),
            "base_parameters": {
              "Destination experiment name": dst_exp_name,
              "DBFS input folder": src_exp_dir
            }
        }
        return self._run_job(nb_name, notebook_task)

    
    def run_job(self, job_func, name):
        print(f"====== run_job: {name}")
        res = job_func()
        run_id = res["run_id"]
        workflow_client.wait_until_cluster_is_created_for_run(run_id)
        workflow_client.wait_until_run_is_done(run_id)
        run = workflow_client.get_run(run_id)
        self._dump_json("Run - final",run)
        return run
    

    def _import_notebook(self, nb_name, src_dir, dst_dir):
        src = os.path.join(src_dir, nb_name)
        dst = os.path.join(dst_dir, nb_name.replace(".py",""))
        self.ws_api.import_workspace(src, dst, "PYTHON", "SOURCE", True)
    

    def _import_notebooks(self, src_dir, dst_dir):
        self.ws_api.import_workspace_dir(src_dir, dst_dir, True, True)
    
    
    def _ws_mkdir(self, ws_base_dir):
        self.ws_api.mkdirs(ws_base_dir)


    def _mk_ws_path(self, ws_object_name):
        return os.path.join(self.ws_base_dir, ws_object_name)


    def _mk_dbfs_path(self, file):
        return os.path.join(self.dst_exp_base_dir, file)


    def _mk_run_name(self, nb_name):
        return f"{self.run_name_prefix}_{nb_name}"


    def _mk_imported_exp_name(self):
        return f"{self.ml_exp_path}_imported"
    

    def _ws_list(self, path):
        lst = self.ws_api.list_objects(path)
        print(f"Workspace objects for {path}:")
        for x in lst:
            print("  ",x.basename)


    def delete_experiments(self, mlflow_client, prefix):
        """ Delete experiments starting with the prefix """
        exps = mlflow_client.list_experiments()
        for exp in exps:
            if exp.name.startswith(prefix) and (exp.name.endswith("_exp") or exp.name.endswith("_exp_imported")):
                mlflow_client.delete_experiment(exp.experiment_id)
    

    def _dump_json(self, msg, dct):
        print(f"{msg}:")
        print(json.dumps(dct,indent=2)+"\n")
