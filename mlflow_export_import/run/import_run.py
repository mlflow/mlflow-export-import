"""
Imports a run from a directory of zip file.
"""

import os
import time
import yaml
import click
import mlflow
from mlflow.utils.file_utils import TempDir

from mlflow_export_import import utils, click_doc
from mlflow_export_import import mk_local_path
from mlflow_export_import.common.find_artifacts import find_artifacts

class RunImporter():
    def __init__(self, mlflow_client=None, mlmodel_fix=True, use_src_user_id=False, import_mlflow_tags=True, import_metadata_tags=False):
        self.client = mlflow_client or mlflow.tracking.MlflowClient()
        self.mlmodel_fix = mlmodel_fix
        self.use_src_user_id = use_src_user_id
        self.import_mlflow_tags = import_mlflow_tags
        self.import_metadata_tags = import_metadata_tags
        self.in_databricks = "DATABRICKS_RUNTIME_VERSION" in os.environ
        print(f"in_databricks: {self.in_databricks}")
        print(f"importing_into_databricks: {utils.importing_into_databricks()}")

    def import_run(self, exp_name, input):
        print(f"Importing run into experiment '{exp_name}' from '{input}'")
        if input.endswith(".zip"):
            return self.import_run_from_zip(exp_name, input)
        else:
            return self.import_run_from_dir(exp_name, input)

    def import_run_from_zip(self, exp_name, zip_file):
        utils.unzip_directory(zip_file, exp_name, self.import_run_from_dir)
        return "run_id_TODO"

    def import_run_from_dir(self, dst_exp_name, src_run_id):
        mlflow.set_experiment(dst_exp_name)
        dst_exp = self.client.get_experiment_by_name(dst_exp_name)
        #print("Experiment name:",dst_exp_name)
        #print("Experiment ID:",dst_exp.experiment_id)
        src_run_path = os.path.join(src_run_id,"run.json")
        src_run_dct = utils.read_json_file(src_run_path)
        with mlflow.start_run() as run:
            run_id = run.info.run_id
            self.import_run_data(src_run_dct, run_id, src_run_dct["info"]["user_id"])
            path = os.path.join(src_run_id,"artifacts")
            mlflow.log_artifacts(mk_local_path(path))
        if self.mlmodel_fix:
            self.fix_dst_mlmodel_(run.info.run_id)
        return (run_id, src_run_dct["tags"].get(utils.TAG_PARENT_ID,None))

    # Hacky expensive way to fix the run_id in the destination MLmodel file since there is no API to get all model artifacts of a run.
    def fix_dst_mlmodel_(self, run_id):
        mlmodel_paths = find_artifacts(run_id, "", "MLmodel")
        for mlmodel_path in mlmodel_paths:
            local_path = self.client.download_artifacts(run_id, mlmodel_path)
            with open(local_path, "r") as f:
                dct = yaml.load(f)
            #print(f"MLmodel run_id: {dct['run_id']}  artifact: {mlmodel_path}")
            dct["run_id"] = run_id
            with TempDir() as tmp:
                new_local_path = os.path.join(tmp.path(),"MLmodel")
                with open(new_local_path, "w") as f:
                    yaml.dump(dct,f)


    def dump_tags(self, tags, msg=""):
        print(f"Tags {msg} - {len(tags)}:")
        for t in tags: print(f"  {t.key} - {t.value}")

    def import_run_data(self, run_dct, run_id, src_user_id):
        from mlflow.entities import Metric, Param, RunTag
        now = round(time.time())
        params = [ Param(k,v) for k,v in run_dct["params"].items() ]
        metrics = [ Metric(k,v,now,0) for k,v in run_dct["metrics"].items() ] # TODO: missing timestamp and step semantics?

        tags = run_dct["tags"]
        if not self.import_mlflow_tags: # remove mlflow tags
            tags = { k:v for k,v in tags.items() if not k.startswith(utils.TAG_PREFIX_MLFLOW) }
        if not self.import_metadata_tags: # remove mlflow_export_import tags
            tags = { k:v for k,v in tags.items() if not k.startswith(utils.TAG_PREFIX_METADATA) }
        tags = utils.create_mlflow_tags_for_databricks_import(tags) # remove "mlflow" tags that cannot be imported into Databricks

        tags = [ RunTag(k,str(v)) for k,v in tags.items() ]

        #self.dump_tags(tags,"1") # debug
        if not self.in_databricks:
            utils.set_dst_user_id(tags, src_user_id, self.use_src_user_id)
        #self.dump_tags(tags,"2") # debug
        self.client.log_batch(run_id, metrics, params, tags)

@click.command()
@click.option("--input", help="Input path - directory or zip file.", required=True, type=str)
@click.option("--experiment-name", help="Destination experiment name.", required=True, type=str)
@click.option("--mlmodel-fix", help="Add correct run ID in destination MLmodel artifact. Can be expensive for deeply nested artifacts.", type=bool, default=True, show_default=True)
@click.option("--use-src-user-id", help=click_doc.use_src_user_id, type=bool, default=False, show_default=True)
@click.option("--import-mlflow-tags", help=click_doc.import_mlflow_tags, type=bool, default=True, show_default=True)
@click.option("--import-metadata-tags", help=click_doc.import_metadata_tags, type=bool, default=False, show_default=True)

def main(input, experiment_name, mlmodel_fix, use_src_user_id, import_mlflow_tags, import_metadata_tags): # pragma: no cover
    print("Options:")
    for k,v in locals().items():
        print(f"  {k}: {v}")
    importer = RunImporter(None, mlmodel_fix, use_src_user_id, import_mlflow_tags, import_metadata_tags)
    importer.import_run(experiment_name, input)

if __name__ == "__main__":
    main()
