"""
Export a registered model and all the experiment runs associated with each version.
"""

import os
import click
import mlflow

from mlflow_export_import.client.http_client import MlflowHttpClient
from mlflow_export_import.client.http_client import DatabricksHttpClient
from mlflow_export_import.common.click_options import (
    opt_model,
    opt_output_dir,
    opt_notebook_formats,
    opt_stages,
    opt_versions,
    opt_export_latest_versions,
    opt_export_deleted_runs,
    opt_export_permissions,
    opt_export_version_model
)

from mlflow_export_import.common import utils, io_utils, model_utils 
from mlflow_export_import.common.timestamp_utils import fmt_ts_millis
from mlflow_export_import.common import permissions_utils
from mlflow_export_import.common import MlflowExportImportException
from mlflow_export_import.run.export_run import RunExporter

_logger = utils.getLogger(__name__)


def export_model(
        model_name,
        output_dir,
        stages = None,
        versions = None,
        export_latest_versions = False,
        export_version_model = False,
        export_permissions = False,
        export_deleted_runs = False,
        notebook_formats = None,
        mlflow_client = None
    ):
    """
    :param model_name: Registered model name.
    :param output_dir: Export directory.
    :param stages: Stages to export. Default is all stages. Values are Production, Staging, Archived and None.
    :param versions: List of versions to export.
    :param export_latest_versions: Export latest registered model versions instead of all versions.
    :param export_version_model: Export registered model version's 'cached' MLflow model.
    :param export_deleted_runs: Export deleted runs.
    :param export_permissions: Export Databricks permissions.
    :param notebook_formats: List of notebook formats to export. Values are SOURCE, HTML, JUPYTER or DBC.
    :param mlflow_client: MlflowClient
    """

    exporter = ModelExporter(
       notebook_formats = notebook_formats,
       stages = stages,
       versions = versions,
       export_latest_versions = export_latest_versions,
       export_version_model = export_version_model,
       export_permissions = export_permissions,
       export_deleted_runs = export_deleted_runs,
       mlflow_client = mlflow_client
    )
    return exporter.export_model(
        model_name = model_name,
        output_dir = output_dir
    )


class ModelExporter():

    def __init__(self,
            stages = None,
            versions = None,
            export_latest_versions = False,
            export_permissions = False,
            export_deleted_runs = False,
            notebook_formats = None,
            export_version_model = False,
            mlflow_client = None
        ):
        """
        :param mlflow_client: MlflowClient
        :param stages: Stages to export. Default is all stages. Values are Production, Staging, Archived and None.
        :param versions: List of versions to export.
        :param export_latest_versions: Export latest registered model versions instead of all versions.
        :param export_version_model: Export registered model version's 'cached' MLflow model.
        :param notebook_formats: List of notebook formats to export. Values are SOURCE, HTML, JUPYTER or DBC.
        """
        self.mlflow_client = mlflow_client or mlflow.MlflowClient()
        self.http_client = MlflowHttpClient(self.mlflow_client.tracking_uri) 
        self.dbx_client = DatabricksHttpClient(self.mlflow_client.tracking_uri)

        self.run_exporter = RunExporter(self.mlflow_client, export_deleted_runs=export_deleted_runs, notebook_formats=notebook_formats)
        self.stages = self._normalize_stages(stages)
        self.versions = versions if versions else []
        self.export_latest_versions = export_latest_versions
        self.export_permissions = export_permissions
        self.export_version_model = export_version_model
        if len(self.stages) > 0 and len(self.versions) > 0:
            raise MlflowExportImportException(
                f"Both stages {self.stages} and versions {self.versions} cannot be set", http_status_code=400)


    def export_model(self,
            model_name,
            output_dir
        ):
        """
        :param model_name: Registered model name.
        :param output_dir: Output directory.
        :return: Returns bool (if export succeeded) and the model name.
        """
        try:
            self._export_model(model_name, output_dir)
            return True, model_name
        except Exception as e:
            _logger.error(e)
            import traceback
            traceback.print_exc()
            return False, model_name


    def _export_versions(self, versions, output_dir):
        output_versions, failed_versions = ([], [])
        for j,vr in enumerate(versions):
            if len(self.stages) > 0 and not vr.current_stage.lower() in self.stages:
                continue
            if len(self.versions) > 0 and not vr.version in self.versions:
                continue
            self._export_version(vr, output_dir, output_versions, failed_versions, j, len(versions))
        output_versions.sort(key=lambda x: x["version"], reverse=False)
        return output_versions, failed_versions


    def _export_version(self, vr, output_dir, output_versions, failed_versions, j, num_versions):
        opath = os.path.join(output_dir, vr.run_id)
        msg = { "name": vr.name, "version": vr.version, "stage": vr.current_stage }
        _logger.info(f"Exporting model verson {j+1}/{num_versions}: {msg} to '{opath}'")

        try:
            self.run_exporter.export_run(vr.run_id, opath)
            run = self.mlflow_client.get_run(vr.run_id)
            vr_dct = dict(vr)
            vr_dct["_run_artifact_uri"] = run.info.artifact_uri
            experiment = mlflow.get_experiment(run.info.experiment_id)
            vr_dct["_experiment_name"] = experiment.name
            if self.export_version_model:
                vr_dct["_download_uri"] = model_utils.export_version_model(self.mlflow_client, vr, output_dir)
            output_versions.append(vr_dct)

        except mlflow.exceptions.RestException as e:
            err_msg = { "RestException": e.json , "model": vr.name, "version": vr.version, "run_id": vr.run_id }
            if e.json.get("error_code",None) == "RESOURCE_DOES_NOT_EXIST":
                err_msg = { **{"message": "Run probably does not exist"}, **err_msg}
                _logger.error(err_msg)
            else:
                err_msg = { **{"message": "Version cannot be exported"}, **err_msg}
                _logger.error(err_msg)
                import traceback
                traceback.print_exc()
            failed_versions.append(err_msg)


    def _export_model(self, model_name, output_dir):
        ori_versions = model_utils.list_model_versions(self.mlflow_client, model_name, self.export_latest_versions)
        msg = "latest" if self.export_latest_versions else "all"
        _logger.info(f"Exporting model '{model_name}': found {len(ori_versions)} '{msg}' versions")
        versions, failed_versions = self._export_versions(ori_versions, output_dir)

        if utils.importing_into_databricks() and self.export_permissions:
            model = self.http_client.get("databricks/registered-models/get", { "name": model_name })
            model2 = model.pop("registered_model_databricks", None)
            self._adjust_model(model2, versions)
            model2["permissions"] = permissions_utils.get_model_permissions(self.dbx_client, model2["id"])
            model["registered_model"] = model2
        else:
            model = self.http_client.get("registered-models/get", {"name": model_name})
            self._adjust_model(model["registered_model"], versions)

        info_attr = {
            "num_target_stages": len(self.stages),
            "num_target_versions": len(self.versions),
            "num_src_versions": len(versions),
            "num_dst_versions": len(versions),
            "failed_versions": failed_versions,
            "export_latest_versions": self.export_latest_versions,
            "export_permissions": self.export_permissions
        }
        io_utils.write_export_file(output_dir, "model.json", __file__, model, info_attr)
        _logger.info(f"Exported {len(versions)}/{len(ori_versions)} '{msg}' versions for model '{model_name}'")


    def _adjust_model(self, model, versions):
        """ Add nicely formatted timestamps and for aesthetic reasons, line up the dict attributes nicely"""
        self._adjust_timestamp(model, "creation_timestamp")
        self._adjust_timestamp(model, "last_updated_timestamp")
        tags = model.pop("tags", None)
        if tags:
            model["tags"] = tags
        for vr in versions:
            self._adjust_timestamp(vr, "creation_timestamp")
            self._adjust_timestamp(vr, "last_updated_timestamp")
        model["versions"] = versions
        model.pop("latest_versions", None)


    def _adjust_timestamp(self, dct, attr):
        dct[f"_{attr}"] = fmt_ts_millis(dct.get(attr,None))


    def _normalize_stages(self, stages):
        from mlflow.entities.model_registry import model_version_stages
        if stages is None:
            return []
        if isinstance(stages, str):
            if stages == "":
                return []
            stages = stages.split(",")
        stages = [stage.lower() for stage in stages]
        for stage in stages:
            if stage not in model_version_stages._CANONICAL_MAPPING:
                _logger.warning(f"stage '{stage}' must be one of: {model_version_stages.ALL_STAGES}")
        return stages


@click.command()
@opt_model
@opt_output_dir
@opt_stages
@opt_versions
@opt_export_latest_versions
@opt_export_version_model
@opt_export_deleted_runs
@opt_export_permissions
@opt_notebook_formats

def main(model, output_dir, 
        stages, versions, export_latest_versions, 
        export_deleted_runs, 
        export_version_model,
        export_permissions,
        notebook_formats
    ):
    _logger.info("Options:")
    for k,v in locals().items():
        _logger.info(f"  {k}: {v}")
    versions = versions.split(",") if versions else []
    export_model(
        model_name = model,
        output_dir = output_dir,
        stages = stages,
        versions = versions,
        export_latest_versions = export_latest_versions,
        export_deleted_runs = export_deleted_runs,
        export_version_model = export_version_model,
        export_permissions = export_permissions,
        notebook_formats = notebook_formats
    )


if __name__ == "__main__":
    main()
