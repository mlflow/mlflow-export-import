"""
Workflow API Client. Wrapping some low-level REST endpoints with workflow logic.
"""
import sys
import time
import logging
from mlflow_export_import.workflow_api import utils
from databricks_cli.sdk import service

logging.info(f"Python version: {sys.version}")

class WorkflowApiClient(object):
    """ 
    Workflow API Client. Wrapping some low-level REST endpoints with workflow logic.
    """

    def _default_timeout_func(self):
        raise Exception(f"Timeout of {self.timeout_seconds} seconds exceeded")
    

    def __init__(self, profile=None, sleep_seconds=2, timeout_seconds=sys.maxsize, timeout_func=_default_timeout_func, verbose=True):
        """
        :param profile: Databricks profile
        :param sleep_seconds: Seconds to sleep when polling for cluster readiness
        :param timeout_seconds: Timeout in seconds
        :param verbose: To be verbose or not?
        """
        self.sleep_seconds = sleep_seconds
        self.timeout_seconds = timeout_seconds
        self.timeout_func = timeout_func
        self.verbose = verbose

        client = utils.get_api_client(profile)
        self.jobs_service = service.JobsService(client)
        self.cluster_service = service.ClusterService(client)

        self.cluster_noninit_states = { "RUNNING", "TERMINATED", "ERROR", "UNKNOWN" }
        self.run_terminal_states = { "TERMINATED", "SKIPPED", "INTERNAL_ERROR" }

        
    def wait_until_cluster_is_created_for_run(self, run_id):
        """ Wait until cluster_instance for specified run_id is available. """ 
        name = "cluster_is_created"
        def is_done(run_id):
            dct = self.get_run(run_id)
            res = "cluster_instance" in dct
            if res: 
                cluster_id = dct["cluster_instance"]["cluster_id"]
                msg = f"Done waiting for '{name}'. Cluster {cluster_id} has been created for run {run_id}."
            else:
                msg = f"Waiting for '{name}'. run {run_id}."
            return (res,msg,dct)
        return self._wait_until(is_done, run_id, f"Start waiting for '{name}'.")


    def wait_until_cluster_is_running(self, cluster_id):
        """ Wait until cluster state is in RUNNING, TERMINATED, ERROR or UNKNOWN state. """
        name = "cluster is running"
        def is_done(cluster_id):
            dct = self.get_cluster(cluster_id)
            state = dct["state"]
            res = state in self.cluster_noninit_states
            msg0 = f"Cluster {cluster_id} is in {state} state"
            msg = f"Waiting for '{name}'. {msg0}" if res else f"Waiting for '{name}'. {msg0}."
            return (res,msg,dct)
        return self._wait_until(is_done,cluster_id, f"Start waiting for '{name}'")

        
    def run_submit(self, job_spec):
        return self.jobs_service.submit_run(**job_spec)


    def get_run(self, run_id):
        """ Get run details. """
        return self.jobs_service.get_run(run_id)


    def get_run_state(self, run_id):
        """ Get run state. """
        run = self.jobs_service.get_run(run_id)
        return run["state"]


    def wait_until_run_is_done(self, run_id):
        """ Wait until specified run_id is done, i.e. life_cycle_state is either TERMINATED, SKIPPED or INTERNAL_ERROR. """
        name = "run_is_done"
        def is_done(run_id):
            run = self.get_run_state(run_id)
            res = run["life_cycle_state"] in self.run_terminal_states
            msg0 = f"Run {run_id} is in {run['life_cycle_state']} state"
            msg = f"Waiting for '{name}'. {msg0}."
            return (res, msg, run)
        return self._wait_until(is_done, run_id, f"Start waiting for '{name}'. Run {run_id}.")


    def _wait_until(self, func, obj_id, init_msg):
        idx = 0
        start_time = time.time()
        if self.verbose: logging.info(init_msg)
        while True:
            if time.time()-start_time > self.timeout_seconds:
                self.timeout_func(self)
            (res, msg, dct) = func(obj_id)
            time.sleep(self.sleep_seconds)
            if self.verbose: logging.info(msg)
            if res: break
            idx += 1
        num_seconds = time.time() - start_time
        logging.info("Processing time: {0:.2f} seconds".format(num_seconds)) # TODO
        return dct
