""" 
Copies a run from one MLflow server to another.
"""

import time
import click
import mlflow
from mlflow.utils.annotations import deprecated
from mlflow.entities import Metric, Param, RunTag
from mlflow_export_import import utils, click_doc
from mlflow_export_import import BaseCopier, create_client

print("MLflow Version:", mlflow.__version__)
print("MLflow Tracking URI:", mlflow.get_tracking_uri())

@deprecated()
class RunCopier(BaseCopier):
    def __init__(self, src_client, dst_client, use_src_user_id=False, export_metadata_tags=False):
        super().__init__(src_client, dst_client)
        self.use_src_user_id = use_src_user_id
        self.export_metadata_tags = export_metadata_tags

    def copy_run(self, src_run_id, dst_exp_name):
        print("src_run_id:",src_run_id)
        dst_exp = self.get_experiment(self.dst_client,dst_exp_name)
        print("  dst_exp.name:",dst_exp.name)
        print("  dst_exp.id:",dst_exp.experiment_id)
        return self._copy_run(src_run_id, dst_exp.experiment_id)

    def _copy_run(self, src_run_id, dst_experiment_id):
        src_run = self.src_client.get_run(src_run_id)
        dst_run = self.dst_client.create_run(dst_experiment_id) # NOTE: does not set user_id; is 'unknown'
        self._copy_run_data(src_run, dst_run.info.run_id)
        local_path = self.src_client.download_artifacts(src_run_id,"")
        self.dst_client.log_artifacts(dst_run.info.run_id,local_path)
        self.dst_client.set_terminated(dst_run.info.run_id, src_run.info.status)
        return (dst_run.info.run_id, src_run.data.tags.get("mlflow.parentRunId",None))

    def _copy_run_data(self, src_run, dst_run_id):
        now = int(time.time()+.5)
        params = [ Param(k,v) for k,v in src_run.data.params.items() ]
        metrics = [ Metric(k,v,now,0) for k,v in src_run.data.metrics.items() ] # TODO: timestamp and step semantics?
        tags = utils.create_tags_for_metadata(self.src_client, src_run, self.export_metadata_tags)
        tags = [ RunTag(k,str(v)) for k,v in tags.items() ]
        utils.set_dst_user_id(tags, src_run.info.user_id, self.use_src_user_id)
        self.dst_client.log_batch(dst_run_id, metrics, params, tags)

@click.command()
@click.option("--src-uri", 
    help="Source MLflow API URI.",
    type=str,
    required=True
)
@click.option("--dst-uri", 
    help="Destination MLflow API URI.",
    type=str,
    required=True
)
@click.option("--src-run-id",
    help="Source run ID.", 
    type=str,
    required=True
)
@click.option("--dst-experiment-name",
    help="Destination experiment name.", 
    type=str,
    required=True
)
@click.option("--use-src-user-id", 
    help=click_doc.use_src_user_id, 
    type=bool, 
    default=False, 
    show_default=True
)
@click.option("--export-metadata-tags", 
    help=click_doc.export_metadata_tags, 
    type=bool, 
    default=False, 
    show_default=True
)

def main(src_uri, dst_uri, src_run_id, dst_experiment_name, use_src_user_id, export_metadata_tags): # pragma: no cover
    print("Options:")
    for k,v in locals().items():
        print(f"  {k}: {v}")
    src_client = create_client(src_uri)
    dst_client = create_client(dst_uri)
    print("src_client:",src_client)
    print("dst_client:",dst_client)
    src_client = create_client(src_uri)
    dst_client = create_client(dst_uri)
    print("  src_client:",src_client)
    print("  dst_client:",dst_client)
    copier = RunCopier(src_client, dst_client, use_src_user_id, export_metadata_tags)
    copier.copy_run(src_run_id, dst_experiment_name)

if __name__ == "__main__":
    main()
