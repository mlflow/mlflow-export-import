# Databricks notebook source
# MAGIC %sh 
# MAGIC #pip install mlflow-export-import
# MAGIC pip install git+https:///github.com/mlflow/mlflow-export-import/#egg=mlflow-export-import

# COMMAND ----------

import mlflow
mlflow_client = mlflow.MlflowClient()
print("mlflow.version:", mlflow.__version__)

# COMMAND ----------

def mk_dbfs_path(path):
    return path.replace("/dbfs","dbfs:")

def mk_local_path(path):
    return path.replace("dbfs:","/dbfs")

# COMMAND ----------

def get_notebook_formats(num):
    widget_name = f"{num}. Notebook formats"
    all_notebook_formats = [ "SOURCE", "DBC", "HTML", "JUPYTER" ]
    dbutils.widgets.multiselect(widget_name, all_notebook_formats[0], all_notebook_formats)
    notebook_formats = dbutils.widgets.get(widget_name)
    notebook_formats = notebook_formats.split(",")
    if "" in notebook_formats: notebook_formats.remove("")
    return notebook_formats

# COMMAND ----------

def assert_widget(value, name):
    if len(value.rstrip())==0: 
        raise Exception(f"ERROR: '{name}' widget is required")

# COMMAND ----------

from mlflow.utils import databricks_utils
host_name = databricks_utils.get_browser_hostname()
print("host_name:", host_name)

# COMMAND ----------

def display_run_uri(run_id):
    if host_name:
        run = mlflow_client.get_run(run_id)
        uri = f"https://{host_name}/#mlflow/experiments/{run.info.experiment_id}/runs/{run_id}"
        displayHTML("""<b>Run URI:</b> <a href="{}">{}</a>""".format(uri,uri))

# COMMAND ----------

def display_registered_model_uri(model_name):
    if host_name:
        uri = f"https://{host_name}/#mlflow/models/{model_name}"
        displayHTML("""<b>Registered Model URI:</b> <a href="{}">{}</a>""".format(uri,uri))

# COMMAND ----------

def display_registered_model_version_uri(model_name, version):
    if host_name:
        uri = f"https://{host_name}/#mlflow/models/{model_name}/versions/{version}"
        displayHTML("""<b>Registered Model Version URI:</b> <a href="{}">{}</a>""".format(uri,uri))

# COMMAND ----------

def display_experiment_uri(experiment_name):
    if host_name:
        experiment_id = mlflow_client.get_experiment_by_name(experiment_name).experiment_id
        uri = "https://{}/#mlflow/experiments/{}".format(host_name, experiment_id)
        displayHTML("""<b>Experiment URI:</b> <a href="{}">{}</a>""".format(uri,uri))

# COMMAND ----------

def display_experiment_info(experiment_name):
    if host_name:
        experiment_id = mlflow_client.get_experiment_by_name(experiment_name).experiment_id
        experiment = mlflow_client.get_experiment(experiment_id)
        _display_experiment_info(experiment)
    
def _display_experiment_info(experiment):
    host_name = dbutils.notebook.entry_point.getDbutils().notebook().getContext().tags().get("browserHostName").get()
    uri = f"https://{host_name}/#mlflow/experiments/{experiment.experiment_id}"
    displayHTML(f"""
    <font size=”1″ >
    <table cellpadding=5 cellspacing=0 border=1 bgcolor="#FDFEFE" style="font-size:13px;">
    <tr><td colspan=2><b><i>Experiment</i></b></td></tr>
    <tr><td>UI link</td><td><a href="{uri}">{uri}</a></td></tr>
    <tr><td>Name</td><td>{experiment.name}</td></tr>
    <tr><td>ID</td><td>{experiment.experiment_id}</td></tr>
    </table>
     </font>
    """)
