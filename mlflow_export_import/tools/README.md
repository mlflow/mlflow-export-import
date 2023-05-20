# MLflow Export Import Tools - Experimental

## Overview

Experimental WIP.

Tools:
* [Filter one model from export-models directory](#Filter-one-model-from-export-models-directory)
* [Rewrite models and experiments of JSON export directory](#Rewrite-models-and-experiments-of-JSON-export-directory)


## Rewrite models and experiments of JSON export directory

Rewrites each model and experiment JSON file in a bulk export directory with the logic from the pluggable custom rewrite module.

See:
* [rewrite_export.py](rewrite_export.py) - main and core logic
* [custom_export_rewriters.py](samples/custom_export_rewriters.py) - sample custom rewrite logic

A user-provided custom module is specified which will rewrite each model and experiment JSON file.
The rewrite module contains two methods:- model_processor() and experiment_processor().

**Sample custom_export_models_processrs.py**

In this example [custom_export_rewriters.py](samples/custom_export_rewriters.py) we simply truncate the versions and runs to 2 elements respectively.

Rewrites [models.json](https://github.com/mlflow/mlflow-export-import/blob/master/samples/databricks/bulk/models/models/Sklearn_WineQuality/model.json#L22).
```
def process_model(model_dct):
    versions = model_dct["mlflow"]["registered_model"]["versions"]
    versions = versions[:2]
    model_dct["mlflow"]["registered_model"]["versions"] = versions
```

Rewrites [experiment.json](https://github.com/mlflow/mlflow-export-import/blob/master/samples/databricks/bulk/experiments/76bcc705806b407fb971843bfb5e5cae/experiment.json#L22).

```
def process_experiment(experiment_dct):
    runs = experiment_dct["mlflow"]["runs"]
    runs = runs[:2]
    experiment_dct["mlflow"]["runs"] = runs
```


**Example**
```
python -u -m mlflow_export_import.tools.process_export_models \
  --input-dir export_models \
  --custom-rewriters-module mlflow_export_import/tools/samples/custom_export_rewriters.py
```

**Usage**
```
python -u -m mlflow_export_import.tools.process_export_models --help

Options:
  --input-dir TEXT                Export directory of export-models or export-
                                  all.  [required]
  --custom-rewriters-module TEXT  Python file containing user-provided custom
                                  model and experiment rewrite logic. Module
                                  expects 2 methods: rewrite_models(dct) and
                                  rewrite_experiments(dct).  [required]
```

## Filter one model from export-models directory

* Motivation: you have exported a large number of models, and just want to selectively import one model for testing.
* Selects specified model from `export-models` directory and creates a new export directory
with just that model and the experiment that its versions' runs belong to.
* Assumes all model version runs belong to one experiment and exports just that experiment.
* Note: applicable to `exports-all` directory since its directory structure is the same as that of `export-models`.
* Note: applicable to the output of both`export-models` and `exports-all` since their structure is the same.

**Example**

```
python -u -m mlflow_export_import.tools.filter_one_model \
  --input-dir exported/export_models \
  --output-dir out \
  --src-model sklearn_iris_model \
  --dst-model new_iris_model \
  --dst-experiment  new_iris_exp
```

**Usage**
```
python -u -m mlflow_export_import.tools.filter_select_model --help

Options:
  --input-dir TEXT       Input directory  [required]
  --output-dir TEXT      Output directory.  [required]
  --src-model TEXT       Source registered model.  [required]
  --dst-model TEXT       Destination registered model. If not specified use
                         the source model.
  --dst-experiment TEXT  Destination experiment to update. We assum that all
                         version runs belong to one experiment.
```
