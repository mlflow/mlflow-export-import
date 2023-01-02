# MLflow Export Import Limitations


## General Limitations

* Nested runs are only supported when you import an experiment. For a run, it is still a TODO.
* If the run linked to a registered model version does not exist (has been deleted) the version is not exported 
  since when importing [MLflowClient.create_model_version](https://mlflow.org/docs/latest/python_api/mlflow.client.html#mlflow.client.MlflowClient.create_model_version) requires a run ID.
* If you need to preserve registered model version nummbers do not use the `use-threads` option since version numbers will not be exported or imported sequentially.
* Run tags are always exported as a `string` even if they are an `int` since [MlflowClienti.get_run()](https://mlflow.org/docs/latest/python_api/mlflow.client.html#mlflow.client.MlflowClient.get_run)  does not return tag type information.
* Importing from a file-based `--backend-store-uri` implementation is not supported since it does not have the same semantics as a database-based implementation (e.g. primary key constraints are not respected, model registry is not implemented, etc.).
This is is not a limitation of mlflow-export-import but rather of the MLflow file-based implementation which is not meant for production.
`

## Databricks Limitations

A Databricks MLflow run is associated with a notebook that generated the model.

There are two types of Databricks notebooks:
* Workspace notebooks. These are the classical notebooks whose source of truth is the Databricks internal database.
Every run has system tags 'XX' that points to:
  * XX:
  * XX:
* Git Repo notebooks. These are the new Git-based notebooks whose source of truth is a git repo.

### Workspace Notebooks

#### Exporting Workspace Notebook Revisions
* The notebook revision associated with a run can be exported. It is stored as an artifact in the run's `notebooks` artifact directory.
*  You can save the notebook in the suppported SOURCE, HTML, JUPYTER and DBC formats. 
*  Examples: `notebooks/notebook.dbc` or `notebooks/notebook.source`.

#### Importing Workspace Notebooks

* Partial functionality due to Databricks REST API limitations.
* The Databricks REST API does not support:
  * Importing a notebook with its revision history.
  * Linking an imported run with its associated imported notebook revision.
* The API does allow you to export a notebook revision, but it is simply a notebook with one revision. 
* The notebook is exported as a run artifact for convenience.
* When you import a run, the link to its source `notebookRevisionID` tag will be a dead link and you cannot access the notebook from the MLflow UI.
See the `dst-notebook-dir` option for `Import Run`.
* As another convenience, the import tools allows you to import the exported notebook into a Databricks workspace directory. 
For more details, see:
  *  [README_single - Import run](README_single.md#Import-run)
  *  [README_single - Import experiment](README_single.md#Import-experiment)
* You must export a notebook in the SOURCE format for the notebook to be imported.


### Used ID
* When importing a run or experiment, for open source (OSS) MLflow you can specify a different user owner. 
* OSS MLflow - the destination run `mlflow.user` tag can be the same as the source `mlflow.user` tag since OSS MLflow allows you to set this tag.
* Databricks MLflow - you cannot set the `mlflow.user` tag.  The `mlflow.user` will be based upon the personal access token (PAT) of the importing user.

