# MLflow Export Import - Bulk Tools

## Overview

**TLDR**
* Tools that copy models and their versions' runs along with the runs' experiment.
* Original source model and experiment names are preserved.
* Leverages the [point tools](README_point.md) as basic building blocks.

**Bulk tools**
* `export-all` - exports all the MLflow objects of the tracking server.
* `export-models` - exports registered models and their versions' backing run along with the experiment that the run belongs to.
* `import-models` - imports models and their runs and experiments from the above exported directory.

**Top-level output directory structure of an export**
```
+---experiments
+---models
```

For further directory structure see the `point` tool sections for experiments and models further below.

## Export the entire MLflow tracking server

Export all models, experiments and runs as well as a run's Databricks notebook (best effort).

Source: [export_all.py](mlflow_export_import/bulk/export_all.py).

### Usage
```
Options:
  --output-dir TEXT               Output directory.  [required]
  --notebook-formats TEXT         Notebook formats. Values are SOURCE, HTML,
                                  JUPYTER or DBC (comma seperated).  [default: ]
  --export-notebook-revision BOOLEAN
                                  Export the run's notebook revision.
                                  Experimental not yet publicly available.
                                  [default: False]
```
### Examples

```
export-all --output-dir
```

## Export models with versions' runs and runs' experiment


Exports registered models and their versions' backing run along with the experiment that the run belongs to.

The `export-all-runs` option is of particular significance. 
It controls whether all runs of an experiment are exported or only those associated with a registered model version.
Obviously there are many runs that are not linked to a registered model version.
This can make a substantial difference in export time.

Source: [export_models.py](mlflow_export_import/bulk/export_models.py).

### Usage
```
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
```

### Examples

#### Export all models

```
export-models --output-dir out
```

#### Export specified models
```
export-models \
  --output-dir out \
  --models sklearn-wine,sklearn-iris
```

#### Export models starting with prefix
```
export-models \
  --output-dir out \
  --models sklearn*
```

## Import models and experiments

Source: [import_models.py](mlflow_export_import/bulk/import_models.py).

### Usage
```
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
```

### Examples
```
import-models  --input-dir out
```
