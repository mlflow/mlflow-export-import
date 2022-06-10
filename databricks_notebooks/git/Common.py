# Databricks notebook source
# MAGIC %sh pip install git+https:///github.com/mlflow/mlflow-export-import/#egg=mlflow-export-import

# COMMAND ----------

host_name = dbutils.notebook.entry_point.getDbutils().notebook().getContext().tags().get("browserHostName").get()
import mlflow
client = mlflow.tracking.MlflowClient()

# COMMAND ----------

def display_run_uri(run_id):
    run = mlflow.get_run(run_id)
    uri = f"https://{host_name}/#mlflow/experiments/{run.info.experiment_id}/runs/{run.info.run_id}"
    displayHTML("""<b>Run URI:</b> <a href="{}">{}</a>""".format(uri,uri))

# COMMAND ----------

def display_registered_model_uri(model_name):
    uri = f"https://{host_name}/#mlflow/models/{model_name}"
    displayHTML("""<b>Registered Model URI:</b> <a href="{}">{}</a>""".format(uri,uri))

# COMMAND ----------

def _display_experiment_uri(experiment_id):
    uri = "https://{}/#mlflow/experiments/{}".format(host_name, experiment_id)
    displayHTML("""<b>Experiment URI:</b> <a href="{}">{}</a>""".format(uri,uri))

# COMMAND ----------

def display_experiment_uri(experiment_name):
    experiment_id = client.get_experiment_by_name(experiment_name).experiment_id
    uri = "https://{}/#mlflow/experiments/{}".format(host_name, experiment_id)
    displayHTML("""<b>Experiment URI:</b> <a href="{}">{}</a>""".format(uri,uri))

# COMMAND ----------

def find_run_dir(output_dir, env_var_name, file_name):
    import glob
    files = [f for f in glob.glob(f"{output_dir}/*") if not f.endswith(file_name)]
    os.environ[env_var_name] = files[0]
    return files[0]