# MLflow Export Import - Collection Tools

## Overview

High-level tools to copy an entire tracking server or the collection of MLflow objects (runs, experiments and registered models).
Full object referential integrity is maintained as well as the original MLflow object names.

Three types of Collection tools:
* All - all MLflow objects of the tracking server.
* Registered models - models and their versions' run and the run's experiment.
* Experiments.

Notes:
* Original source model and experiment names are preserved.
* Leverages the [Individual tools](README_individual.md) as basic building blocks.

### Tools

| MLflow Object | Documentation | Code | Description |
|-------|-------|----|---|
| **_All_**  | [export-all](#Export-all-MLflow-objects) | [code](mlflow_export_import/bulk/export_all.py) | Exports all MLflow objects (registered models, experiments and runs) to a directory. |
| | [import-all](#Import-all-MLflow-objects) | Uses [import-models](mlflow_export_import/bulk/import_models.py) | Imports MLflow objects from a directory. |
| **_Model_** | [export-models](#Export-registered-models) | [code](mlflow_export_import/bulk/export_models.py) | Exports several (or all) registered models and their versions' backing run along with the run's experiment to a directory. |
| | [import-models](#Import-registered-models) | [code](mlflow_export_import/bulk/import_models.py) | Imports registered models from a directory. |
| **_Experiment_** | [export-experiments](#Export-experiments) | [code](mlflow_export_import/bulk/export_experiments.py) | Export several (or all) experiments to a directory. |
| | [import-experiments](#Import-experiments) | [code](mlflow_export_import/bulk/import_experiments.py) | Imports experiments from a directory. |

## Overview - Old

## All MLflow Objects Tools

### Export all MLflow objects

Exports all MLflow objects of the tracking server (Databricks workspace) - all models, experiments and runs.
If you are exporting from Databricks the notebook is also exported.

Source: [export_all.py](mlflow_export_import/bulk/export_all.py).

#### Usage
```
export-all --help

Options:
  --output-dir TEXT             Output directory.  [required]
  --export-source-tags BOOLEAN  Export source run information (RunInfo, MLflow
                                system tags starting with 'mlflow' and
                                metadata) under the 'mlflow_export_import' tag
                                prefix. See README.md for more details.
                                [default: False]
  --notebook-formats TEXT       Databricks notebook formats. Values are
                                SOURCE, HTML, JUPYTER or DBC (comma
                                seperated).
  --use-threads BOOLEAN         Process export/import in parallel using
                                threads.  [default: False]
  --help                        Show this message and exit.
```
#### Example

```
export-all --output-dir out
```

### Import all MLflow objects

`import-all` is a console script that invokes [import-models](#Import-registered-models) to import all exported MLflow objects.
The exported output directory is the same structure for both `export-all` and `export-models`.

#### Examples
```
import-all --input-dir out
```

## Registered Models Tools

Tools that copy registered models and their versions' runs along with the runs' experiment.

When exporting a registered models the associated following objects will be exported:
* All the latest versions of a model.
* The run associated with each version.
* The experiment that the run belongs to.

**Scripts**
* `export-models` - exports registered models and their versions' backing run along with the experiment that the run belongs to.
* `import-models` - imports models and their runs and experiments from the above exported directory.

**Output directory structure of models export**

```
+-manifest.json
|
+-experiments/
| +-manifest.json
| +-1/
| | +-manifest.json
| | +-5bd3b8a44faf4803989544af5cb4d66e/
| | | +-run.json
| | | +-artifacts/
| | | | +-sklearn-model/
| | | |   +-requirements.txt
| | | |   +-python_env.yaml
| | | |   +-model.pkl
| | | |   +-conda.yaml
| | | |   +-MLmodel
| | +-4273c31c45744ec385f3654c63c31360
| | | +-run.json
| | | . . .
| 
+-models/
| +-manifest.json
| +-sklearn_iris/
| | +-model.json
```

| +-4273c31c45744ec385f3654c63c31360/
| | +-run.json

For further directory structure see the `individual` tool sections for experiments and models further below.


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
  --output-dir TEXT             Output directory.  [required]
  --models TEXT                 Models to export. Values are 'all', comma
                                seperated list of models or model prefix with
                                * ('sklearn*'). Default is 'all'
  --export-source-tags BOOLEAN  Export source run information (RunInfo, MLflow
                                system tags starting with 'mlflow' and
                                metadata) under the 'mlflow_export_import' tag
                                prefix. See README.md for more details.
                                [default: False]
  --notebook-formats TEXT       Databricks notebook formats. Values are
                                SOURCE, HTML, JUPYTER or DBC (comma
                                seperated).
  --stages TEXT                 Stages to export (comma seperated). Default is
                                all stages. Values are Production, Staging,
                                Archived and None.
  --export-all-runs BOOLEAN     Export all runs of experiment or just runs
                                associated with registered model versions.
  --use-threads BOOLEAN         Process export/import in parallel using
                                threads.  [default: False]
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
  --input-dir TEXT                Input directory.  [required]
  --delete-model BOOLEAN          First delete the model if it exists and all
                                  its versions.  [default: False]
  --verbose BOOLEAN               Verbose.  [default: False]
  --use-src-user-id BOOLEAN       Set the destination user ID to the source
                                  user ID. Source user ID is ignored when
                                  importing into Databricks since setting it
                                  is not allowed.  [default: False]
  --use-threads BOOLEAN           Process the export/import in parallel using
                                  threads.  [default: False]
```

#### Examples
```
import-models  --input-dir out
```

## Experiments 

Export/import experiments to a directory.

**Output directory structure of models export**
```
+-manifest.json

+-manifest.json
| +-5bd3b8a44faf4803989544af5cb4d66e/
| | +-run.json
| | +-artifacts/
| | | +-sklearn-model/
| | |   +-requirements.txt
| | |   +-python_env.yaml
| | |   +-model.pkl
| | |   +-conda.yaml
| | |   +-MLmodel
| +-4273c31c45744ec385f3654c63c31360/
| | +-run.json
| | +- . . .
```

### Export Experiments Tools

Export several (or all) experiments to a directory.

#### Usage
```
export-experiments --help

Options:
  --experiments TEXT            Experiment names or IDs (comma delimited).
                                'all' will export all experiments.
                                [required]
  --output-dir TEXT             Output directory.  [required]
  --export-source-tags BOOLEAN  Export source run information (RunInfo, MLflow
                                system tags starting with 'mlflow' and
                                metadata) under the 'mlflow_export_import' tag
                                prefix. See README.md for more details.
                                [default: False]
  --notebook-formats TEXT       Databricks notebook formats. Values are
                                SOURCE, HTML, JUPYTER or DBC (comma
                                seperated).
  --use-threads BOOLEAN         Process export/import in parallel using
                                threads.  [default: False]
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

The output directory contains a manifest file and a subdirectory for each experiment (by experiment ID).

Each experiment subdirectory in turn contains its own manifest file and a subdirectory for each run.
The run directory contains a run.json file containing run metadata and artifact directories.

In the example below we have two experiments - 1 and 7. Experiment 1 (sklearn) has two runs (f4eaa7ddbb7c41148fe03c530d9b486f and 5f80bb7cd0fc40038e0e17abe22b304c) whereas experiment 7 (sparkml) has one run (ffb7f72a8dfb46edb4b11aed21de444b).

```
+-manifest.json
+-1/
| +-manifest.json
| +-f4eaa7ddbb7c41148fe03c530d9b486f/
| | +-run.json
| | +-artifacts/
| |   +-plot.png
| |   +-sklearn-model/
| |   | +-model.pkl
| |   | +-conda.yaml
| |   | +-MLmodel
| |   +-onnx-model/
| |     +-model.onnx
| |     +-conda.yaml
| |     +-MLmodel
| +-5f80bb7cd0fc40038e0e17abe22b304c/
| | +-run.json
|   +-artifacts/
|     +-plot.png
|     +-sklearn-model/
|     | +-model.pkl
|     | +-conda.yaml
|     | +-MLmodel
|     +-onnx-model/
|       +-model.onnx
|       +-conda.yaml
|       +-MLmodel
+-7/
| +-manifest.json
| +-ffb7f72a8dfb46edb4b11aed21de444b/
| | +-run.json
|   +-artifacts/
|     +-spark-model/
|     | +-sparkml/
|     |   +-stages/
|     |   +-metadata/
|     +-mleap-model/
|       +-mleap/
|         +-model/
```

Sample:
```
{
  "info": {
    "mlflow_version": "1.11.0",
    "mlflow_tracking_uri": "http://localhost:5000",
    "export_time": "2020-09-10 20:23:45"
  },
  "experiments": [
    {
      "id": "1",
      "name": "sklearn"
    },
    {
      "id": "7",
      "name": "sparkml"
    }
  ]
}
```

Sample:

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
  --input-dir TEXT                Input directory.  [required]
  --experiment-name-prefix TEXT   If specified, added as prefix to experiment name.
  --use-src-user-id BOOLEAN       Set the destination user ID to the source
                                  user ID. Source user ID is ignored when
                                  importing into Databricks since setting it
                                  is not allowed.  [default: False]
  --use-threads BOOLEAN           Process the export/import in parallel using
                                  threads.  [default: False]
```

#### Examples

```
import-experiments --input-dir out 
```

```
import-experiments \
  --input-dir out \
  --experiment-name-prefix imported_
```
