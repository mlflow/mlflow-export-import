# Databricks notebook source
# MAGIC %sh 
# MAGIC #pip install mlflow-export-import
# MAGIC pip install git+https:///github.com/mlflow/mlflow-export-import/#egg=mlflow-export-import

# COMMAND ----------

import mlflow
client = mlflow.client.MlflowClient()

# COMMAND ----------

host_name = dbutils.notebook.entry_point.getDbutils().notebook().getContext().tags().get("browserHostName")
#if host_name is not None: # NOTE: Weird. host_name is None when running as job, but this "if" doesn't work!
if str(host_name) != "None":
    host_name = host_name.get()
host_name

# COMMAND ----------

def display_run_uri(run_id):
    if host_name:  
        run = mlflow.get_run(run_id)
        uri = f"https://{host_name}/#mlflow/experiments/{run.info.experiment_id}/runs/{run.info.run_id}"
        displayHTML("""<b>Run URI:</b> <a href="{}">{}</a>""".format(uri,uri))

# COMMAND ----------

def display_registered_model_uri(model_name):
    if host_name:
        uri = f"https://{host_name}/#mlflow/models/{model_name}"
        displayHTML("""<b>Registered Model URI:</b> <a href="{}">{}</a>""".format(uri,uri))

# COMMAND ----------

def display_experiment_uri(experiment_name):
    if host_name:
        experiment_id = client.get_experiment_by_name(experiment_name).experiment_id
        uri = "https://{}/#mlflow/experiments/{}".format(host_name, experiment_id)
        displayHTML("""<b>Experiment URI:</b> <a href="{}">{}</a>""".format(uri,uri))

# COMMAND ----------

def find_run_dir(output_dir, env_var_name, file_name):
    import glob
    files = [f for f in glob.glob(f"{output_dir}/*") if not f.endswith(file_name)]
    os.environ[env_var_name] = files[0]
    return files[0]

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

import mlflow
print("mlflow.version:",mlflow.__version__)

# COMMAND ----------

def assert_widget(value, name):
    if len(value.rstrip())==0: 
        raise Exception(f"ERROR: '{name}' widget is required")