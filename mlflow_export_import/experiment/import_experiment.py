import click
from mlflow_export_import import peek_at_experiment
from mlflow_export_import.experiment.import_experiments import ExperimentImporter

@click.command()
@click.option("--input-dir", help="Input path - directory", required=True, type=str)
@click.option("--experiment-name", help="Destination experiment name", required=True, type=str)
@click.option("--just-peek", help="Just display experiment metadata - do not import", type=bool, default=False)
@click.option("--use-src-user-id", help="Use source user ID", type=bool, default=False)
@click.option("--import-mlflow-tags", help="Import mlflow tags", type=bool, default=True)
@click.option("--import-metadata-tags", help="Import mlflow_export_import tags", type=bool, default=False)

def main(input_dir, experiment_name, just_peek, use_src_user_id, import_mlflow_tags, import_metadata_tags): # pragma: no cover
    print("Options:")
    for k,v in locals().items():
        print(f"  {k}: {v}")
    if just_peek:
        peek_at_experiment(input_dir)
    else:
        importer = ExperimentImporter(None, use_src_user_id, import_mlflow_tags, import_metadata_tags)
        importer.import_experiment(experiment_name, input_dir)

if __name__ == "__main__":
    main()
