import os
import json
import mlflow
from databricks_cli.sdk import service

from mlflow_export_import.common import mlflow_utils
from mlflow_export_import.workflow_api.workflow_api_client import WorkflowApiClient
from mlflow_export_import.client import databricks_utils

from databricks_cli.workspace.api import WorkspaceApi
from databricks_cli.dbfs.api import DbfsApi, DbfsPath
from databricks_cli.clusters.api import ClusterApi

print(f"MLflow Tracking URI: {mlflow.get_tracking_uri()}")
mlflow_client = mlflow.tracking.MlflowClient()
print(f"mlflow_client: {mlflow_client}")

workflow_client = WorkflowApiClient()
print(f"workflow_client: {workflow_client}")

_formats = [ "SOURCE" ]
_export_src_tags = "yes"

_experiment_nb = "Iris_Train"
_experiment_name = "Iris_Train_exp"

_fs_nb_base_dir = "../../databricks_notebooks/single"
_fs_experiment_nb_name = "Iris_Train.py" 
_fs_experiment_nb_path = os.path.join("experiment", _fs_experiment_nb_name)
print(f"_fs_experiment_nb_path: {_fs_experiment_nb_path}")


class DatabricksTester():
    def __init__(self, 
            ws_base_dir, 
            dbfs_base_export_dir, 
            local_artifacts_compare_dir, 
            cluster_spec, 
            model_name, 
            run_name_prefix, 
            verbose=False
        ):
        api_client = databricks_utils.get_api_client()
        self.ws_api = WorkspaceApi(api_client)
        self.dbfs_api = DbfsApi(api_client)
        self.cluster_api = ClusterApi(api_client)
        self.jobs_service = service.JobsService(api_client)

        self.ws_base_dir = ws_base_dir
        self.dbfs_base_export_dir = dbfs_base_export_dir
        self.local_artifacts_compare_dir = local_artifacts_compare_dir
        self.output_run_base_dir = os.path.join(dbfs_base_export_dir, "runs")
        self.output_exp_base_dir = os.path.join(dbfs_base_export_dir, "experiments")
        self.output_model_base_dir = os.path.join(dbfs_base_export_dir, "models")

        self.model_name = model_name
        self.run_name_prefix = run_name_prefix
        self.verbose = verbose
        self.cluster_spec = cluster_spec
        self.cluster_id = self._get_cluster_id()

        self.ml_nb_path = self._mk_ws_path(_experiment_nb)
        self.ml_exp_path = self._mk_ws_path(_experiment_name)
        print(f"ML training notebook: {self.ml_nb_path}")
        print(f"ML training experiment: {self.ml_exp_path}")

        self._init_dirs()


    def run_export_run_job(self):
        run = mlflow_utils.get_first_run(mlflow_client, self.ml_exp_path)
        nb_name = "Export_Run"
        nb_path = self._mk_ws_path(nb_name)
        notebook_task = {
            "notebook_path": nb_path,
            "base_parameters": {
              "1. Run ID": run.info.run_id,
              "2. Output base directory": self.output_run_base_dir
            }
        }
        return self._run_job(nb_name, notebook_task)


    def run_export_experiment_job(self):
        nb_name = "Export_Experiment"
        nb_path = self._mk_ws_path(nb_name)
        notebook_task = { 
            "notebook_path": nb_path,
            "base_parameters": {
              "1. Experiment ID or Name": self.ml_exp_path,
              "2. Output base directory": self.output_exp_base_dir
            }
        }
        return self._run_job(nb_name, notebook_task)


    def run_export_model_job(self):
        nb_name = "Export_Model"
        nb_path = self._mk_ws_path(nb_name)
        notebook_task = { 
            "notebook_path": nb_path,
            "base_parameters": {
              "1. Model": self.model_name,
              "2. Output base directory": self.output_model_base_dir
            }
        }
        return self._run_job(nb_name, notebook_task)


    def run_import_run_job(self):
        nb_name = "Import_Run"
        files = self.dbfs_api.list_files(DbfsPath(self.output_run_base_dir))
        run_id = files[0].dbfs_path.basename
        src_run_dir = os.path.join(self.output_run_base_dir, run_id)
        dst_exp_name = self.mk_imported_name(self.ml_exp_path+"_run")
        notebook_task = {
            "notebook_path": self._mk_ws_path(nb_name),
            "base_parameters": {
              "1. Destination experiment name": dst_exp_name,
              "2. Input directory": src_run_dir
            }
        }
        return self._run_job(nb_name, notebook_task)


    def run_import_experiment_job(self):
        nb_name = "Import_Experiment"
        exp = mlflow_client.get_experiment_by_name(self.ml_exp_path)
        assert exp
        dst_exp_name = self.mk_imported_name(self.ml_exp_path)
        src_exp_dir = self._mk_dbfs_path(self.output_exp_base_dir, exp.experiment_id)
        notebook_task = {
            "notebook_path": self._mk_ws_path(nb_name),
            "base_parameters": {
              "1. Destination experiment name": dst_exp_name,
              "2. Input directory": src_exp_dir
            }
        }
        return self._run_job(nb_name, notebook_task)


    def run_import_model_job(self):
        nb_name = "Import_Model"
        export_model_dir = self._mk_dbfs_path(self.output_model_base_dir, self.model_name)
        dst_model_name = self.mk_imported_name(self.model_name)
        dst_exp_name = self.mk_imported_name(self.ml_exp_path)
        notebook_task = {
            "notebook_path": self._mk_ws_path(nb_name),
            "base_parameters": {
              "1. Model name": dst_model_name,
              "2. Destination experiment name": dst_exp_name,
              "3. Input directory": export_model_dir
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


    def run_job(self, job_func, name):
        print(f"====== run_job: {name}")
        res = job_func()
        run_id = res["run_id"]
        workflow_client.wait_until_cluster_is_created_for_run(run_id)
        workflow_client.wait_until_run_is_done(run_id)
        run = workflow_client.get_run(run_id)
        self._dump_json("Run - final",run)
        return run


    def _run_job(self, nb_name, notebook_task):
        run_name = self._mk_run_name(nb_name)
        if self.verbose:
            self._dump_json(f"Run job {run_name} - notebook_task", notebook_task)
        return self.jobs_service.submit_run(run_name, existing_cluster_id=self.cluster_id, notebook_task=notebook_task)
    

    def _init_dirs(self):
        """
        Create/cleanup test Databricks workspace and DBFS directories.
        Copy notebooks to workspace test directory.
        """

        # Delete workspace and DBFS directorues
        self._delete_dirs()

        # Create and load workspace with notebooks
        self.ws_api.mkdirs(self.ws_base_dir)
        self._ws_list(self.ws_base_dir)
        self._import_notebook(_fs_experiment_nb_name, "experiment", self.ws_base_dir) # import the model training notebook
        self._import_notebooks(_fs_nb_base_dir, self.ws_base_dir) # import all the export-import notebooks

        # Create DBFS export directory
        self.dbfs_api.mkdirs(DbfsPath(self.dbfs_base_export_dir))


    def _import_notebook(self, nb_name, src_dir, dst_dir):
        src = os.path.join(src_dir, nb_name)
        dst = os.path.join(dst_dir, nb_name.replace(".py",""))
        self.ws_api.import_workspace(src, dst, "PYTHON", "SOURCE", True)
    

    def _import_notebooks(self, src_dir, dst_dir):
        self.ws_api.import_workspace_dir(src_dir, dst_dir, True, True)
    
    
    def _mk_ws_path(self, ws_object_name):
        return os.path.join(self.ws_base_dir, ws_object_name)


    def _mk_dbfs_path(self, dir, file):
        return os.path.join(dir, file)


    def _mk_run_name(self, nb_name):
        return f"{self.run_name_prefix}_{nb_name}"


    def mk_imported_name(self, name):
        return f"{name}_imported"
    

    def _ws_list(self, path):
        lst = self.ws_api.list_objects(path)
        print(f"Workspace objects for {path}:")
        for x in lst:
            print(f"   {x.basename}")


    def _ws_delete(self):
        try:
            self.ws_api.delete(self.ws_base_dir, is_recursive=True)
        except Exception:
            pass


    def _delete_dirs(self):
        """ Delete both test workspace and DBFS directories """
        self._ws_delete()
        self.dbfs_api.delete(DbfsPath(self.dbfs_base_export_dir), recursive=True)


    def _delete_cluster(self):
        if isinstance(self.cluster_spec, dict):
            print(f"Deleting cluster {self.cluster_id}")
            self.cluster_api.permanent_delete(self.cluster_id)


    def teardown(self):
        self._delete_dirs()
        self._delete_cluster()


    def _get_cluster_id(self):
        if isinstance(self.cluster_spec, str):
            cluster_id = self.cluster_spec
        elif isinstance(self.cluster_spec, dict):
            cluster = self.cluster_api.create_cluster(self.cluster_spec)
            cluster_id = cluster["cluster_id"]
        else:
            raise Exception(f"Unknown cluster type: {type(self.cluster_spec)}. Must be a string or dict.")
        cluster = self.cluster_api.get_cluster(cluster_id)
        print(f"Using cluster: id={cluster_id} name={cluster['cluster_name']}")
        return cluster_id


    def _dump_json(self, msg, dct):
        print(f"{msg}:")
        print(json.dumps(dct,indent=2)+"\n")
