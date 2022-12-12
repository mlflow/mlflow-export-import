""" 
Exports an experiment to a directory.
"""

import os
import click
import mlflow

from mlflow_export_import.common import mlflow_utils
from mlflow_export_import.common.iterators import SearchRunsIterator
from mlflow_export_import.common import io_utils
from mlflow_export_import.run.export_run import RunExporter
from mlflow_export_import.common import utils, click_doc


class ExperimentExporter():

    def __init__(self, mlflow_client, notebook_formats=None):
        """
        :param mlflow_client: MLflow client.
        :param notebook_formats: List of notebook formats to export. Values are SOURCE, HTML, JUPYTER or DBC.
        """
        self.mlflow_client = mlflow_client
        self.run_exporter = RunExporter(self.mlflow_client, notebook_formats=notebook_formats)


    def export_experiment(self, exp_id_or_name, output_dir, run_ids=None):
        """
        :param exp_id_or_name: Experiment ID or name.
        :param output_dir: Output directory.
        :param run_ids: List of run IDs to export. If None export all run IDs.
        :return: Number of successful and number of failed runs.
        """
        exp = mlflow_utils.get_experiment(self.mlflow_client, exp_id_or_name)
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

        custom_info = {
            "num_total_runs": (j+1),
            "num_ok_runs": len(ok_run_ids),
            "ok_runs": ok_run_ids,
            "num_failed_runs": len(failed_run_ids),
            "failed_runs": failed_run_ids
        }
        content = { "experiment": utils.strip_underscores(exp) } 
        io_utils.write_manifest_file(output_dir, "experiment.json", content, custom_info)

        msg = f"for experiment '{exp.name}' (ID: {exp.experiment_id})"
        if len(failed_run_ids) == 0:
            print(f"All {len(ok_run_ids)} runs succesfully exported {msg}")
        else:
            print(f"{len(ok_run_ids)/j} runs succesfully exported {msg}")
            print(f"{len(failed_run_ids)/j} runs failed {msg}")
        return len(ok_run_ids), len(failed_run_ids) 


    def _export_run(self, idx, run, output_dir, ok_run_ids, failed_run_ids):
        run_dir = os.path.join(output_dir, run.info.run_id)
        print(f"Exporting run {idx+1}: {run.info.run_id}")
        res = self.run_exporter.export_run(run.info.run_id, run_dir)
        if res:
            ok_run_ids.append(run.info.run_id)
        else:
            failed_run_ids.append(run.info.run_id)


@click.command()
@click.option("--experiment",
    help="Experiment name or ID.", 
    type=str,
    required=True
)
@click.option("--output-dir",
    help="Output directory.", 
    type=str,
    required=True
)
@click.option("--notebook-formats",
    help=click_doc.notebook_formats, 
    type=str, 
    default="", 
    show_default=True
)
def main(experiment, output_dir, notebook_formats):
    print("Options:")
    for k,v in locals().items():
        print(f"  {k}: {v}")
    client = mlflow.tracking.MlflowClient()
    exporter = ExperimentExporter(
        client,
        notebook_formats=utils.string_to_list(notebook_formats))
    exporter.export_experiment(experiment, output_dir)

if __name__ == "__main__":
    main()
