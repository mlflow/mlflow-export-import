# Databricks notebook source
# MAGIC %md ### Export Experiment
# MAGIC
# MAGIC #### Overview
# MAGIC * Exports an experiment and its runs to a directory.
# MAGIC * Output file `experiment.json` contains top-level experiment metadata.
# MAGIC * Each run and its artifacts are stored as a sub-directory whose name is that of the run_id.
# MAGIC * Notebooks can be exported in several formats.
# MAGIC
# MAGIC ##### Output folder
# MAGIC ```
# MAGIC
# MAGIC +-experiment.json
# MAGIC +-d2309e6c74dc4679b576a37abf6b6af8/
# MAGIC | +-run.json
# MAGIC | +-artifacts/
# MAGIC |   +-sklearn-model/
# MAGIC |   | +-model.pkl
# MAGIC |   | +-conda.yaml
# MAGIC |   | +-MLmodel
# MAGIC ```
# MAGIC
# MAGIC ##### Widgets
# MAGIC * `1. Experiment ID or name` - Either the experiment ID or experiment name.
# MAGIC * `2. Output base directory` - Base output directory of the exported experiment. All the experiment data will be saved here under the experiment ID sub-directory.	
# MAGIC * `3. Run start date` - Export runs after this UTC date (inclusive). Example: `2023-04-05`.
# MAGIC * `4. Export permissions` - Export Databricks permissions.
# MAGIC * `5. Notebook formats` - Standard Databricks notebook formats such as SOURCE, HTML, JUPYTER, DBC. See [Databricks Export Format](https://docs.databricks.com/dev-tools/api/latest/workspace.html#notebookexportformat) documentation.
# MAGIC * `6. Run IDs` - comma-seperated list of runs to export. Default is to export all runs.
# MAGIC * `7. Check nested runs` - If true, will export all the runs of a nested run specified in above run ID list.
# MAGIC
# MAGIC See: https://github.com/mlflow/mlflow-export-import/blob/master/mlflow_export_import/experiment/export_experiment.py.

# COMMAND ----------

# MAGIC %md ### Include setup

# COMMAND ----------

# MAGIC %run ./Common

# COMMAND ----------

# MAGIC %md ### Widget setup

# COMMAND ----------

dbutils.widgets.text("1. Experiment ID or Name", "") 
experiment_id_or_name = dbutils.widgets.get("1. Experiment ID or Name")
 
dbutils.widgets.text("2. Output base directory", "") 
output_dir = dbutils.widgets.get("2. Output base directory")

dbutils.widgets.text("3. Run start date", "") 
run_start_date = dbutils.widgets.get("3. Run start date")
if run_start_date=="": run_start_date = None

dbutils.widgets.dropdown("4. Export permissions","no",["yes","no"])
export_permissions = dbutils.widgets.get("4. Export permissions") == "yes"

notebook_formats = get_notebook_formats(5)

dbutils.widgets.text("6. Run IDs", "") 
run_ids = dbutils.widgets.get("6. Run IDs")
if run_ids:
    run_ids = run_ids.split(",")

dbutils.widgets.dropdown("7. Check nested runs","no",["yes","no"])
check_nested_runs = dbutils.widgets.get("7. Check nested runs") == "yes"

print("experiment_id_or_name:", experiment_id_or_name)
print("output_dir:", output_dir)
print("run_start_date:", run_start_date)
print("export_permissions:", export_permissions)
print("run_ids:", run_ids)
print("notebook_formats:", notebook_formats)
print("check_nested_runs:", check_nested_runs)

# COMMAND ----------

assert_widget(experiment_id_or_name, "1. Experiment ID or Name")
assert_widget(output_dir, "2. Output base directory")

# COMMAND ----------

from mlflow_export_import.common import mlflow_utils 

experiment = mlflow_utils.get_experiment(mlflow_client, experiment_id_or_name)
output_dir = f"{output_dir}/{experiment.experiment_id}"

print("experiment_id:", experiment.experiment_id)
print("experiment_name:", experiment.name)       
print("output_dir:", output_dir)

# COMMAND ----------

# MAGIC %md ### Display experiment UI link

# COMMAND ----------

display_experiment_info(experiment.name)

# COMMAND ----------

# MAGIC %md ### Export the experiment

# COMMAND ----------

from mlflow_export_import.experiment.export_experiment import export_experiment

export_experiment(
    experiment_id_or_name = experiment.experiment_id,
    output_dir = output_dir,
    run_start_time = run_start_date,
    run_ids = run_ids,
    check_nested_runs = check_nested_runs,
    export_permissions = export_permissions,
    notebook_formats = notebook_formats
)

# COMMAND ----------

# MAGIC %md ### Display exported JSON

# COMMAND ----------

import os
output_dir = mk_local_path(output_dir)
os.environ['OUTPUT_DIR'] = output_dir
output_dir

# COMMAND ----------

# MAGIC %sh echo $OUTPUT_DIR

# COMMAND ----------

# MAGIC %sh ls -lR $OUTPUT_DIR

# COMMAND ----------

# MAGIC %sh cat $OUTPUT_DIR/experiment.json
