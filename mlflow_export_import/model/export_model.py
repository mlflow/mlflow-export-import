"""
Export a registered model and all the experiment runs associated with each version.
"""

import os
import click
import mlflow
from mlflow_export_import.common.http_client import HttpClient
from mlflow_export_import.common import filesystem as _filesystem
from mlflow_export_import.run.export_run import RunExporter
from mlflow_export_import import utils

class ModelExporter():
    def __init__(self, export_metadata_tags=False, notebook_formats=["SOURCE"], filesystem=None, stages=None):
        self.fs = filesystem or _filesystem.get_filesystem()
        self.client = mlflow.tracking.MlflowClient()
        self.client2 = HttpClient("api/2.0/mlflow")
        self.run_exporter = RunExporter(self.client, export_metadata_tags=export_metadata_tags, notebook_formats=notebook_formats, filesystem=filesystem)
        self.stages = self.normalize_stages(stages)

    def export_model(self, output_dir, model_name):
        path = os.path.join(output_dir,"model.json")
        model = self.client2.get(f"registered-models/get?name={model_name}")
        model["registered_model"]["latest_versions"] = []
        versions = self.client.search_model_versions(f"name='{model_name}'")
        print(f"Found {len(versions)} versions")
        for vr in versions:
            if len(self.stages) > 0 and not vr.current_stage.lower() in self.stages:
                continue
            run_id = vr.run_id
            opath = os.path.join(output_dir,run_id)
            opath = opath.replace("dbfs:","/dbfs")
            print(f"Exporting version {vr.version} stage '{vr.current_stage}' with run_id {run_id} to {opath}")
            try:
                self.run_exporter.export_run(run_id, opath)
                run = self.client.get_run(run_id)
                dct = dict(vr)
                dct["artifact_uri"] = run.info.artifact_uri
                model["registered_model"]["latest_versions"].append(dct)
            except mlflow.exceptions.RestException as e:
                if "RESOURCE_DOES_NOT_EXIST: Run" in str(e):
                    print(f"WARNING: Run for version {vr.version} does not exist. {e}")
                else:
                    import traceback
                    traceback.print_exc()
        utils.write_json_file(self.fs, path, model)

    def normalize_stages(self, stages):
        from mlflow.entities.model_registry import model_version_stages
        if stages is None:
            return []
        if isinstance(stages,str):
            stages = stages.split(",")
        stages = [ stage.lower() for stage in stages ]
        for stage in stages:
            if stage not in model_version_stages._CANONICAL_MAPPING:
                print(f"WARNING: stage '{stage}' must be one of: {model_version_stages.ALL_STAGES}")
        return stages

@click.command()
@click.option("--model", help="Registered model name.", required=True, type=str)
@click.option("--output-dir", help="Output directory.", required=True, type=str)
@click.option("--stages", help="Stages to export (comma seperated). Default is all stages.", required=None, type=str)

def main(model, output_dir, stages): # pragma: no cover
    print("Options:")
    for k,v in locals().items():
        print(f"  {k}: {v}")
    exporter = ModelExporter(stages=stages)
    exporter.export_model(output_dir, model)

if __name__ == "__main__":
    main()
