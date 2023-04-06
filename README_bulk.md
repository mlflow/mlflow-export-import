# MLflow Export Import - Bulk Object Tools

## Overview

High-level tools to copy an entire tracking server or a collection of MLflow objects (runs, experiments and registered models).
Full object referential integrity is maintained as well as the original MLflow object names.

Three types of bulk tools:
* All - all MLflow objects of the tracking server.
* Registered models - models and their versions' run and the run's experiment.
* Experiments.

Notes:
* Original source model and experiment names are preserved.
* Leverages the [Single tools](README_single.md) as basic building blocks.

### Tools

| MLflow Object | Documentation | Code | Description |
|-------|-------|----|---|
| All  | [export-all](#Export-all-MLflow-objects) | [code](mlflow_export_import/bulk/export_all.py) | Exports all MLflow objects (registered models, experiments and runs) to a directory. |
| | [import-all](#Import-all-MLflow-objects) | Uses [import-models](mlflow_export_import/bulk/import_models.py) | Imports MLflow objects from a directory. |
| Model | [export-models](#Export-registered-models) | [code](mlflow_export_import/bulk/export_models.py) | Exports several (or all) registered models and their versions' backing run along with the run's experiment to a directory. |
| | [import-models](#Import-registered-models) | [code](mlflow_export_import/bulk/import_models.py) | Imports registered models from a directory. |
| Experiment | [export-experiments](#Export-experiments) | [code](mlflow_export_import/bulk/export_experiments.py) | Export several (or all) experiments to a directory. |
| | [import-experiments](#Import-experiments) | [code](mlflow_export_import/bulk/import_experiments.py) | Imports experiments from a directory. |


## All MLflow Objects Tools

### Export all MLflow objects

Exports all MLflow objects of the tracking server (Databricks workspace) - all models, experiments and runs.
If you are exporting from Databricks, the notebook can be exported in several different formats.

Source: [export_all.py](mlflow_export_import/bulk/export_all.py).

#### Usage
```
export-all --help

Options:
  --output-dir TEXT               Output directory.  [required]
  --export-latest-versions BOOLEAN
                                  Export latest registered model versions
                                  instead of all versions.  [default: False]
  --stages TEXT                   Stages to export (comma seperated). Default
                                  is all stages and all versions. Stages are
                                  Production, Staging, Archived and None.
                                  Mututally exclusive with option --versions.
  --export-permissions BOOLEAN    Export Databricks permissions.  [default:
                                  False]
  --run-start-time TEXT           Only export runs started after this UTC time
                                  (inclusive). Format: YYYY-MM-DD.
  --notebook-formats TEXT         Databricks notebook formats. Values are
                                  SOURCE, HTML, JUPYTER or DBC (comma
                                  seperated).
  --use-threads BOOLEAN           Process in parallel using threads.
                                  [default: False]
```
#### Example

```
export-all --output-dir out
```

### Import all MLflow objects

`import-all` imports all exported MLflow objects.
Since the exported output directory is the same structure for both `export-all` and `export-models`, this script calls [import-models](#Import-registered-models).

#### Examples
```
import-all --input-dir out
```

## Registered Models

Copy registered models and transitively all the objects that the model versions depend on: runs and their experiments.

See also [Single tools Registered Model Tools](README_single.md#registered-model-tools).

When exporting a registered models the following model's associated objects are also transitively exported:
* All the versions of a model.
* The run associated with each version.
* The experiment that the run belongs to. 

**Scripts**
* `export-models` - exports registered models and their versions' backing run along with the experiment that the run belongs to.
* `import-models` - imports models and their versions' runs and experiments from the above exported directory.


**Output directory**

See [sample JSON export](samples/databricks/bulk/models).

```
+-manifest.json
|
+-models/
| +-models.json
| +-Sklearn_WineQuality/
| | +-model.json
| +-Keras_MNIST/
| | +-model.json
|
+-experiments/
| +-experiments.json
| +-1/
| | +-experiment.json
| | | . . .
```


### Export registered models 

Exports registered models and their versions' backing run along with the run's experiment.

The `export-all-runs` option is of particular significance. 
It controls whether all runs of an experiment are exported or only those associated with a registered model version.
Obviously there are many runs that are not linked to a registered model version.
This can make a substantial difference in export time.

Source: [export_models.py](mlflow_export_import/bulk/export_models.py).

#### Usage
```
export-models --help

Options:
  --output-dir TEXT               Output directory.  [required]
  --models TEXT                   Registered model names (comma delimited).
                                  For example, 'model1,model2'. 'all' will
                                  export all models.  [required]
  --export-latest-versions BOOLEAN
                                  Export latest registered model versions
                                  instead of all versions.  [default: False]
  --export-all-runs BOOLEAN       Export all runs of experiment or just runs
                                  associated with registered model versions.
                                  [default: False]
  --stages TEXT                   Stages to export (comma seperated). Default
                                  is all stages and all versions. Stages are
                                  Production, Staging, Archived and None.
                                  Mututally exclusive with option --versions.
  --export-permissions BOOLEAN    Export Databricks permissions.  [default:
                                  False]
  --notebook-formats TEXT         Databricks notebook formats. Values are
                                  SOURCE, HTML, JUPYTER or DBC (comma
                                  seperated).
  --use-threads BOOLEAN           Process in parallel using threads.
                                  [default: False]
```

#### Examples

##### Export all models

```
export-models --output-dir out
```

##### Export specified models
```
export-models \
  --output-dir out \
  --models sklearn-wine,sklearn-iris
```

##### Export models starting with prefix
```
export-models \
  --output-dir out \
  --models sklearn*
```

### Import registered models 

Source: [import_models.py](mlflow_export_import/bulk/import_models.py).

#### Usage
```
import-models --help

Options:
  --input-dir TEXT              Input path - directory  [required]
  --delete-model BOOLEAN        If the model exists, first delete the model
                                and all its versions.  [default: False]
  --use-src-user-id BOOLEAN     Set the destination user field to the source
                                user field.  Only valid for open source
                                MLflow.  When importing into Databricks, the
                                source user field is ignored since it is
                                automatically picked up from your Databricks
                                access token.  There is no MLflow API endpoint
                                to explicity set the user_id for Run and
                                Registered Model.
  --verbose BOOLEAN             Verbose.  [default: False]
  --import-source-tags BOOLEAN  Import source information for registered model
                                and its versions ad tags in destination
                                object.  [default: False]
  --use-threads BOOLEAN           Process in parallel using threads.
                                  [default: False]
```

#### Examples
```
import-models  --input-dir out
```

## Experiments 

Export/import experiments to a directory.

**Output directory**
```
+-experiments.json
| +-5bd3b8a44faf4803989544af5cb4d66e/
| | +-run.json
| | +-artifacts/
| | | +-sklearn-model/
| +-4273c31c45744ec385f3654c63c31360/
| | +-run.json
| | +-artifacts/
| | +- . . .
```

### Export Experiments

Export several (or all) experiments to a directory.

#### Usage
```
export-experiments --help

  --experiments TEXT            Experiment names or IDs (comma delimited).
                                For example, 'sklearn_wine,sklearn_iris' or
                                '1,2'. 'all' will export all experiments.
                                [required]
  --output-dir TEXT             Output directory.  [required]
  --export-permissions BOOLEAN  Export Databricks permissions.  [default:
                                False]
  --run-start-time TEXT         Only export runs started after this UTC time
                                (inclusive). Format: YYYY-MM-DD.
  --notebook-formats TEXT       Databricks notebook formats. Values are
                                SOURCE, HTML, JUPYTER or DBC (comma
                                seperated).
  --use-threads BOOLEAN         Process in parallel using threads.
                                Experimental: needs improved logging.
                                [default: False]
```

#### Examples

Export experiments by experiment ID.
```
export-experiments \
  --experiments 2,3 --output-dir out
```

Export experiments by experiment name.
```
export-experiments \
  --experiments sklearn,sparkml --output-dir out
```

Export all experiments.
```
export-experiments \
  --experiments all --output-dir out
```

```
Exporting experiment 'Default' (ID 0) to 'out/0'
Exporting experiment 'sklearn' (ID 1) to 'out/1'
Exporting experiment 'keras_mnist' (ID 2) to 'out/2'
. . .

249 experiments exported
1770/1770 runs succesfully exported
Duration: 1.6 seonds
```

#### Export directory structure

The root output directory contains an experiments.json file and a subdirectory for each experiment (named for the experiment ID).

Each experiment subdirectory in turn contains its own experiment.json file and a subdirectory for each run.
The run directory contains a run.json file containing run metadata and artifact directories.

In the example below we have two experiments - 1 and 7. Experiment 1 (sklearn) has two runs (f4eaa7ddbb7c41148fe03c530d9b486f and 5f80bb7cd0fc40038e0e17abe22b304c) whereas experiment 7 (sparkml) has one run (ffb7f72a8dfb46edb4b11aed21de444b).

```
+-experiments.json
+-1/
| +-experiment.json
| +-f4eaa7ddbb7c41148fe03c530d9b486f/
| | +-run.json
| | +-artifacts/
| |   +-sklearn-model/
| |   +-onnx-model/
| +-5f80bb7cd0fc40038e0e17abe22b304c/
| | +-run.json
|   +-artifacts/
|     +-sklearn-model/
|     +-onnx-model/
+-7/
| +-experiment.json
| +-ffb7f72a8dfb46edb4b11aed21de444b/
| | +-run.json
|   +-artifacts/
|     +-spark-model/
|     +-mleap-model/
```

Sample experiments.json
```
{
  "system": {
    "package_version": "1.1.2",
    "script": "export_experiments.py"
  },
  "info": {
    "duration": 0.2,
    "experiments": 3,
    "total_runs": 2,
    "ok_runs": 2,
    "failed_runs": 0
  },
  "mlflow": {
    "experiments": [
      {
        "id": "2",
        "name": "sklearn",
        "ok_runs": 1,
        "failed_runs": 0,
        "duration": 0.1
      },
      {
        "id": "2",
        "name": "sparkml",
        "ok_runs": 1,
        "failed_runs": 0,
        "duration": 0.1
      },
```

Sample experiment.json
```
{
  "system": {
    "package_version": "1.1.2",
  }
  "info": {
    "num_total_runs": 1,
    "num_ok_runs": 1,
    "num_failed_runs": 0,
    "failed_runs": []
  },
  "mlflow": {
    "experiment": {
      "experiment_id": "1",
      "name": "sklearn_wine",
      "artifact_location": "/Users/andre.mesarovic/work/mlflow_server/local_mlrun/mlruns/1",
      "lifecycle_stage": "active",
      "tags": {
        "experiment_created": "2022-12-15 02:17:43",
        "version_mlflow": "2.0.1"
      },
      "creation_time": 1671070664091,
      "last_update_time": 1671070664091
    }
    "runs": [
      "a83cebbccbca41299360c695c5ea72f3"
    ],
  }
```

Sample experiment.json
```
{
  "experiment": {
    "experiment_id": "1",
    "name": "sklearn",
    "artifact_location": "/opt/mlflow/server/mlruns/1",
    "lifecycle_stage": "active"
  },
  "export_info": {
    "export_time": "2022-01-14 03:26:42",
    "num_total_runs": 2,
    "num_ok_runs": 2,
    "ok_runs": [
      "4445f19b7bf04d0fb0173424db476198",
      "d835e17257ad4d6db92441ad93bec549"
    ],
    "num_failed_runs": 0,
    "failed_runs": []
  }
}
```

### Import experiments

Import experiments from a directory. Reads the manifest file to import expirements and their runs.

The experiment will be created if it does not exist in the destination tracking server. 
If the experiment already exists, the source runs will be added to it.


#### Usage

```
import-experiments --help

Options:
  --input-dir TEXT                Input directory  [required]
  --import-source-tags BOOLEAN    Import source information for registered
                                  model and its versions ad tags in
                                  destination object.  [default: False]
  --use-src-user-id BOOLEAN       Set the destination user field to the source
                                  user field.  Only valid for open source
                                  MLflow.  When importing into Databricks, the
                                  source user field is ignored since it is
                                  automatically picked up from your Databricks
                                  access token.  There is no MLflow API
                                  endpoint to explicity set the user_id for
                                  Run and Registered Model.
  --experiment-name-replacements-file TEXT
                                  File with experiment names replacements:
                                  comma-delimited line such as
                                  'old_name,new_name'.
  --use-threads BOOLEAN           Process in parallel using threads.
                                  [default: False]
```



#### Examples

```
import-experiments \
  --input-dir exported_experiments
```

Replace `/Users/me@mycompany.com` with `/Users/you@mycompany.com` in experiment name.
```
import-experiments \
  --input-dir exported_experiments \
  --experiment-name-replacements-file experiment-names.csv
```

```
cat experiment-names.csv

/Users/me@mycompany.com,/Users/you@mycompany.com
/Users/foo@mycompany.com,/Users/bar@mycompany.com
```
