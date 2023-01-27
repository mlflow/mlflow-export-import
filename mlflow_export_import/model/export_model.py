"""
Export a registered model and all the experiment runs associated with each version.
"""

import os
import click
import mlflow

from mlflow_export_import.common import utils
from mlflow_export_import.common import io_utils
#from mlflow_export_import.common.click_options import *
from mlflow_export_import.common.click_options import opt_model, opt_output_dir, \
    opt_notebook_formats, opt_stages, opt_versions
from mlflow_export_import.common import MlflowExportImportException
from mlflow_export_import.common.http_client import MlflowHttpClient
from mlflow_export_import.run.export_run import RunExporter


class ModelExporter():

    def __init__(self,  mlflow_client, notebook_formats=None, stages=None, versions=None, export_run=True):
        """
        :param mlflow_client: MlflowClient
        :param notebook_formats: List of notebook formats to export. Values are SOURCE, HTML, JUPYTER or DBC.
        :param stages: Stages to export. Default is all stages. Values are Production, Staging, Archived and None.
        :param export_run: Export the run that generated a registered model's version.
        """
        self.mlflow_client = mlflow_client
        self.http_client = MlflowHttpClient()
        self.run_exporter = RunExporter(self.mlflow_client, notebook_formats=notebook_formats)
        self.export_run = export_run
        self.stages = self._normalize_stages(stages)
        self.versions = versions if versions else []
        if len(self.stages) > 0 and len(self.versions) > 0:
            raise MlflowExportImportException(f"Both stages {self.stages} and versions {self.versions} cannot be set")


    def export_model(self, model_name, output_dir):
        """
        :param model_name: Registered model name.
        :param output_dir: Output directory.
        :return: Returns bool (if export succeeded) and the model name.
        """
        try:
            self._export_model(model_name, output_dir)
            return True, model_name
        except Exception as e:
            print("ERROR: export_model:", e)
            return False, model_name


    def _export_model(self, model_name, output_dir):
        output_versions = []
        versions = self.mlflow_client.search_model_versions(f"name='{model_name}'")
        print(f"Found {len(versions)} versions for model '{model_name}'")
        manifest = []
        exported_versions = 0
        for vr in versions:
            if len(self.stages) > 0 and not vr.current_stage.lower() in self.stages:
                continue
            if len(self.versions) > 0 and not vr.version in self.versions:
                continue
            opath = os.path.join(output_dir, vr.run_id)
            opath = opath.replace("dbfs:", "/dbfs")
            dct = { "version": vr.version, "stage": vr.current_stage, 
                "run_id": vr.run_id,
                "description": vr.description, "tags": vr.tags }
            print(f"Exporting model '{model_name}' version {vr.version} stage '{vr.current_stage}' to '{opath}'")
            manifest.append(dct)
            try:
                if self.export_run:
                    self.run_exporter.export_run(vr.run_id, opath)
                run = self.mlflow_client.get_run(vr.run_id)
                dct = dict(vr)
                dct["_run_artifact_uri"] = run.info.artifact_uri
                experiment = mlflow.get_experiment(run.info.experiment_id)
                dct["_experiment_name"] = experiment.name
                output_versions.append(dct)
                exported_versions += 1
            except mlflow.exceptions.RestException as e:
                if "RESOURCE_DOES_NOT_EXIST: Run" in str(e):
                    print(f"WARNING: Run for version {vr.version} does not exist. {e}")
                else:
                    import traceback
                    traceback.print_exc()
        output_versions.sort(key=lambda x: x["version"], reverse=False)

        model = self.http_client.get(f"registered-models/get", {"name": model_name})
        model["registered_model"]["latest_versions"] = output_versions

        info_attr = {
            "num_target_stages": len(self.stages),
            "num_target_versions": len(self.versions),
            "num_src_versions": len(versions),
            "num_dst_versions": len(output_versions)
        }
        io_utils.write_export_file(output_dir, "model.json", __file__, model, info_attr)

        print(f"Exported {exported_versions}/{len(output_versions)} versions for model '{model_name}'")
        return manifest


    def _normalize_stages(self, stages):
        from mlflow.entities.model_registry import model_version_stages
        if stages is None:
            return []
        if isinstance(stages, str):
            stages = stages.split(",")
        stages = [stage.lower() for stage in stages]
        for stage in stages:
            if stage not in model_version_stages._CANONICAL_MAPPING:
                print(f"WARNING: stage '{stage}' must be one of: {model_version_stages.ALL_STAGES}")
        return stages


@click.command()
@opt_model
@opt_output_dir
@opt_notebook_formats
@opt_stages
@opt_versions

def main(model, output_dir, notebook_formats, stages, versions):
    print("Options:")
    for k,v in locals().items():
        print(f"  {k}: {v}")
    mlflow_client = mlflow.client.MlflowClient()
    versions = versions.split(",") if versions else []
    exporter = ModelExporter(mlflow_client, notebook_formats=utils.string_to_list(notebook_formats), stages=stages, versions=versions)
    exporter.export_model(model, output_dir)


if __name__ == "__main__":
    main()
