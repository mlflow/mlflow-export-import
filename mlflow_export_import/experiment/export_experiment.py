""" 
Exports an experiment to a directory.
"""

import os
import click
import mlflow

from mlflow_export_import.common.click_options import (
    opt_experiment,
    opt_output_dir,  
    opt_notebook_formats,
    opt_export_permissions
)
from mlflow_export_import.common.iterators import SearchRunsIterator
from mlflow_export_import.common import utils, io_utils, mlflow_utils
from mlflow_export_import.common import permissions_utils
from mlflow_export_import.common.timestamp_utils import fmt_ts_millis
from mlflow_export_import.run.export_run import export_run


def export_experiment(
        experiment_id_or_name,
        output_dir,
        run_ids = None,
        export_permissions = False,
        notebook_formats = None,
        mlflow_client = None
    ):
    """
    :param experiment_id_or_name: Experiment ID or name.
    :param output_dir: Output directory.
    :param run_ids: List of run IDs to export. If None export then all run IDs.
    :param notebook_formats: List of notebook formats to export. Values are SOURCE, HTML, JUPYTER or DBC.
    :param mlflow_client: MLflow client.
    :return: Number of successful and number of failed runs.
    """
    exporter = ExperimentExporter(
        mlflow_client = mlflow_client,
        export_permissions = export_permissions,
        notebook_formats = notebook_formats
    )
    return exporter.export_experiment(
        experiment_id_or_name = experiment_id_or_name,
        output_dir = output_dir,
        run_ids = run_ids
    )


class ExperimentExporter():

    def __init__(self,
            mlflow_client = None,
            export_permissions = False,
            notebook_formats = None
        ):
        """
        :param mlflow_client: MLflow client.
        :param notebook_formats: List of notebook formats to export. Values are SOURCE, HTML, JUPYTER or DBC.
        """
        self.mlflow_client = mlflow_client or mlflow.client.MlflowClient()
        self.export_permissions = export_permissions
        self.notebook_formats = notebook_formats


    def export_experiment(self,
            experiment_id_or_name,
            output_dir,
            run_ids = None
        ):
        """
        :param experiment_id_or_name: Experiment ID or name.
        :param output_dir: Output directory.
        :param run_ids: List of run IDs to export. If None export all run IDs.
        :return: Number of successful and number of failed runs.
        """
        exp = mlflow_utils.get_experiment(self.mlflow_client, experiment_id_or_name)
        print(f"Exporting experiment '{exp.name}' (ID {exp.experiment_id}) to '{output_dir}'")
        ok_run_ids = []
        failed_run_ids = []
        j = -1
        if run_ids:
            for j,run_id in enumerate(run_ids):
                run = self.mlflow_client.get_run(run_id)
                self._export_run(j, run, output_dir, ok_run_ids, failed_run_ids)
        else:
            for j,run in enumerate(SearchRunsIterator(self.mlflow_client, exp.experiment_id)):
                self._export_run(j, run, output_dir, ok_run_ids, failed_run_ids)

        info_attr = {
            "num_total_runs": (j+1),
            "num_ok_runs": len(ok_run_ids),
            "num_failed_runs": len(failed_run_ids),
            "failed_runs": failed_run_ids
        }
        exp_dct = utils.strip_underscores(exp) 
        exp_dct["_creation_time"] = fmt_ts_millis(exp.creation_time)
        exp_dct["_last_update_time"] = fmt_ts_millis(exp.last_update_time)
        exp_dct["tags"] = dict(sorted(exp_dct["tags"].items()))

        mlflow_attr = { "experiment": exp_dct , "runs": ok_run_ids }
        if utils.importing_into_databricks() and self.export_permissions:
            permissions_utils.add_experiment_permissions(exp.experiment_id, mlflow_attr)
        io_utils.write_export_file(output_dir, "experiment.json", __file__, mlflow_attr, info_attr)

        msg = f"for experiment '{exp.name}' (ID: {exp.experiment_id})"
        if j==0:
            print(f"WARNING: No runs exported {msg}")
        elif len(failed_run_ids) == 0:
            print(f"All {len(ok_run_ids)} runs succesfully exported {msg}")
        else:
            print(f"{len(ok_run_ids)/j} runs succesfully exported {msg}")
            print(f"{len(failed_run_ids)/j} runs failed {msg}")
        return len(ok_run_ids), len(failed_run_ids) 


    def _export_run(self, idx, run, output_dir, ok_run_ids, failed_run_ids):
        run_dir = os.path.join(output_dir, run.info.run_id)
        print(f"Exporting run {idx+1}: {run.info.run_id} of experiment {run.info.experiment_id}")
        is_success = export_run(
            run_id = run.info.run_id,
            output_dir = run_dir,
            notebook_formats = self.notebook_formats,
            mlflow_client = self.mlflow_client
        )
        if is_success:
            ok_run_ids.append(run.info.run_id)
        else:
            failed_run_ids.append(run.info.run_id)


@click.command()
@opt_experiment
@opt_output_dir
@opt_export_permissions
@opt_notebook_formats

def main(experiment, output_dir, export_permissions, notebook_formats):
    print("Options:")
    for k,v in locals().items():
        print(f"  {k}: {v}")
    export_experiment(
        experiment_id_or_name = experiment,
        output_dir = output_dir,
        export_permissions = export_permissions,
        notebook_formats = utils.string_to_list(notebook_formats)
    )


if __name__ == "__main__":
    main()
