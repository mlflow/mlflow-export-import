# MLflow Export Import - Bulk Tools

## Overview

Three types of bulk tools:
* All - all MLflow objects of the tracking server.
* Registered models - models and their versions' runs and experiments.
* Experiments.

Notes:
* Original source model and experiment names are preserved.
* Leverages the [point tools](README_point.md) as basic building blocks.


## All MLflow objects

### Export

**Note: WIP.**

Exports all MLflow objects of the tracking server (Databricks workspace) - all models, experiments and runs as well as a run's Databricks notebook (best effort).

Source: [export_all.py](mlflow_export_import/bulk/export_all.py).

#### Usage
```
export-all --help

Options:
  --output-dir TEXT               Output directory.  [required]
  --notebook-formats TEXT         Notebook formats. Values are SOURCE, HTML,
                                  JUPYTER or DBC (comma seperated).  [default: ]
  --export-notebook-revision BOOLEAN
                                  Export the run's notebook revision.
                                  Experimental not yet publicly available.
                                  [default: False]
  --use-threads BOOLEAN           Process the export/import in parallel using
                                  threads.  [default: False]
```
#### Example

```
export-all --output-dir out
```

### Import

Use the `import-models` script described below in the `Import registerd models` section.

```
import-models --input-dir out
```

## Registered models

Tools that copy models and their versions' runs along with the runs' experiment.

**Scripts**
* `export-models` - exports registered models and their versions' backing run along with the experiment that the run belongs to.
* `import-models` - imports models and their runs and experiments from the above exported directory.

**Top-level output directory structure of an export**

```
+---experiments
+---models
```

For further directory structure see the `point` tool sections for experiments and models further below.


### Export registered models 


Exports registered models and their versions' backing run along with the experiment that the run belongs to.

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
  --models TEXT                   Models to export. Values are 'all', comma
                                  seperated list of models or model prefix
                                  with * ('sklearn*'). Default is 'all'
  --stages TEXT                   Stages to export (comma seperated). Default
                                  is all stages. Values are Production,
                                  Staging, Archived and None.
  --notebook-formats TEXT         Notebook formats. Values are SOURCE, HTML,
                                  JUPYTER or DBC (comma seperated).  [default: ]
  --export-all-runs BOOLEAN       Export all runs of experiment or just runs
                                  associated with registered model versions.
  --export-notebook-revision BOOLEAN
                                  Export the run's notebook revision.
                                  Experimental not yet publicly available.
                                  [default: False]
  --use-threads BOOLEAN           Process the export/import in parallel using
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
  --import-mlflow-tags BOOLEAN    Import mlflow tags.  [default: False]
  --import-metadata-tags BOOLEAN  Import mlflow_export_import tags.  [default:
                                  False]
  --use-threads BOOLEAN           Process the export/import in parallel using
                                  threads.  [default: False]
```

#### Examples
```
import-models  --input-dir out
```

## Experiments 

Export/import experiments to a directory.

### Export experiments

Export several (or all) experiments to a directory.

#### Usage
```
export-experiments --help

Options:
  --experiments TEXT              Experiment names or IDs (comma delimited).
                                  'all' will export all experiments.  [required]
  --output-dir TEXT               Output directory.  [required]
  --export-metadata-tags BOOLEAN  Export source run metadata tags.  [default: False]
  --notebook-formats TEXT         Notebook formats. Values are SOURCE, HTML,
                                  JUPYTER or DBC (comma seperated).  [default: ]
  --export-notebook-revision BOOLEAN
                                  Export the run's notebook revision.
                                  Experimental not yet publicly available.
                                  [default: False]
  --use-threads BOOLEAN           Process the export/import in parallel using
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

Sample [experiments manifest.json](samples/oss_mlflow/experiment_list/manifest.json).
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

Sample [experiment manifest.json](samples/oss_mlflow/experiment_list/1/manifest.json).

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
  --import-mlflow-tags BOOLEAN    Import mlflow tags.  [default: True]
  --import-metadata-tags BOOLEAN  Import mlflow_tools tags.  [default: False]
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
