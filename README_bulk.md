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

| MLflow Object | Documentation                                 | Code                                                             | Description                                                                                                                |
|---------------|-----------------------------------------------|------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------|
| All           | [export-all](#Export-all-MLflow-objects)      | [code](mlflow_export_import/bulk/export_all.py)                  | Exports all MLflow objects (registered models, experiments and runs) to a directory.                                       |
|               | [import-all](#Import-all-MLflow-objects)      | Uses [import-models](mlflow_export_import/bulk/import_models.py) | Imports MLflow objects from a directory.                                                                                   |
| Model         | [export-models](#Export-registered-models)    | [code](mlflow_export_import/bulk/export_models.py)               | Exports several (or all) registered models and their versions' backing run along with the run's experiment to a directory. |
|               | [import-models](#Import-registered-models)    | [code](mlflow_export_import/bulk/import_models.py)               | Imports registered models from a directory.                                                                                |
| Experiment    | [export-experiments](#Export-experiments)     | [code](mlflow_export_import/bulk/export_experiments.py)          | Export several (or all) experiments to a directory.                                                                        |
|               | [import-experiments](#Import-experiments)     | [code](mlflow_export_import/bulk/import_experiments.py)          | Imports experiments from a directory.                                                                                      |
| Logged model  | [export-logged-models](#Export-logged-models) | [code](mlflow_export_import/bulk/export_logged_models.py)        | Exports several (or all) logged models to a directory                                                                      |
|               | [import-logged-models](#Import-logged-models) | [code](mlflow_export_import/bulk/import_logged_models.py)        | Imports logged models from a directory                                                                                     |
| Trace         | [export-traces](#Export-traces)               | [code](mlflow_export_import/bulk/export_traces.py)               | Export several (or all) traces to a directory                                                                              |
|               | [import-traces](#Import-traces)               | [code](mlflow_export_import/bulk/import_traces.py)               | Imports traces from a directory                                                                                            |
| Prompt        | [export-prompts](#Export-prompts)             | [code](mlflow_export_import/bulk/export_prompts.py)              | Export prompts from the MLflow Prompt Registry (MLflow 2.21.0+).                                                           |
|               | [import-prompts](#Import-prompts)             | [code](mlflow_export_import/bulk/import_prompts.py)              | Imports prompts to the MLflow Prompt Registry. |   
| Evaluation Dataset | [export-evaluation-datasets](#Export-evaluation-datasets) | [code](mlflow_export_import/bulk/export_evaluation_datasets.py) | Export GenAI evaluation datasets (MLflow 3.4.0+). |
|               | [import-evaluation-datasets](#Import-evaluation-datasets) | [code](mlflow_export_import/bulk/import_evaluation_datasets.py) | Imports GenAI evaluation datasets. |

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
  --run-start-time TEXT           Only export runs started after this UTC time
                                  (inclusive). Format: YYYY-MM-DD or
                                  YYYY-MM-DD HH:MM:SS.
  --runs-until TEXT                    Only export runs started before this UTC time
                                  (exclusive). Use with --run-start-time to
                                  define a time window. Format: YYYY-MM-DD or
                                  YYYY-MM-DD HH:MM:SS.
  --export-deleted-runs BOOLEAN   Export deleted runs.  [default: False] 
  --export-version-model BOOLEAN  Export registered model version's 'cached'
                                  MLflow model.  [default: False] 
  --export-permissions BOOLEAN    Export Databricks permissions.  [default:
                                  False]
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

#### Usage
```
import-all --help

Options:
  --input-dir TEXT               Input directory.  [required]
  --delete-model BOOLEAN         If the model exists, first delete the model
                                 and all its versions.  [default: False]
  --delete-prompt BOOLEAN        If the prompt exists, first delete the prompt
                                 and all its versions.  [default: False]
  --import-permissions BOOLEAN   Import Databricks permissions using the HTTP
                                 PATCH method.  [default: False]
  --experiment-rename-file TEXT  File with experiment names replacements:
                                 comma-delimited line such as
                                 'old_name,new_name'.
  --model-rename-file TEXT       File with registered model names
                                 replacements: comma-delimited line such as
                                 'old_name,new_name'.
  --import-source-tags BOOLEAN   Import source information for registered
                                 model and its versions ad tags in destination
                                 object.  [default: False]
  --use-src-user-id BOOLEAN      Set the destination user field to the source
                                 user field.  Only valid for open source
                                 MLflow.  When importing into Databricks, the
                                 source user field is ignored since it is
                                 automatically picked up from your Databricks
                                 access token.  There is no MLflow API
                                 endpoint to explicity set the user_id for Run
                                 and Registered Model.  [default: False]
  --use-threads BOOLEAN          Process in parallel using threads.  [default:
                                 False]
```

#### Examples

##### Import all objects
```
import-all --input-dir out
```

##### Import with model deletion (if model exists, delete it first)
```
import-all \
  --input-dir out \
  --delete-model True
```

## Registered Models

Copy registered models and transitively all the objects that the model versions depend on: runs and their experiments.

See also [Single tools Registered Model Tools](README_single.md#registered-model-tools).

When exporting a registered models the following model's associated objects are also transitively exported:
* Versions of a model.
* The run associated with each version.
* The experiment that the run belongs to. 

**Scripts**
* `export-models` - exports registered models.
* `import-models` - imports models.


### Export directory

Export directory samples: 
[open source](samples/oss_mlflow/bulk/models)
\- [Databricks](samples/databricks/bulk/models).

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
| +-1280664374380606/
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
  --models TEXT                   Registered model names (comma delimited)  or
                                  filename ending with '.txt' containing them.
                                  For example, 'model1,model2'. 'all' will
                                  export all models. Or 'models.txt' will
                                  contain a list of model names.  [required]
  --output-dir TEXT               Output directory.  [required]
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
  --export-deleted-runs BOOLEAN   Export deleted runs.  [default: False]
  --export-version-model BOOLEAN  Export registered model version's 'cached'
                                  MLflow model.  [default: False]
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

##### Export models from filename
```
export-models \
  --output-dir out \
  --models my-models.txt
```

where `my-models.txt` is:
```
sklearn_iris
sklearn_wine
```


### Import registered models 

Source: [import_models.py](mlflow_export_import/bulk/import_models.py).

#### Usage
```
import-models --help

Options:
  --input-dir TEXT               Input directory.  [required]
  --delete-model BOOLEAN         If the model exists, first delete the model
                                 and all its versions.  [default: False]
  --import-permissions BOOLEAN   Import Databricks permissions using the HTTP
                                 PATCH method.  [default: False]
  --experiment-rename-file TEXT  File with experiment names replacements:
                                 comma-delimited line such as
                                 'old_name,new_name'.
  --model-rename-file TEXT       File with registered model names
                                 replacements: comma-delimited line such as
                                 'old_name,new_name'.
  --import-source-tags BOOLEAN   Import source information for registered
                                 model and its versions ad tags in destination
                                 object.  [default: False]
  --use-src-user-id BOOLEAN      Set the destination user field to the source
                                 user field.  Only valid for open source
                                 MLflow.  When importing into Databricks, the
                                 source user field is ignored since it is
                                 automatically picked up from your Databricks
                                 access token.  There is no MLflow API
                                 endpoint to explicity set the user_id for Run
                                 and Registered Model.  [default: False]
  --use-threads BOOLEAN          Process in parallel using threads.  [default:
                                 False]
```

#### Examples
```
import-models  --input-dir out
```

## Experiments 

Export/import experiments to a directory.

### Export Directory 

Export directory samples: 
[open source](samples/oss_mlflow/bulk/experiments)
\- [Databricks](samples/databricks/bulk/experiments).

**Export directory**
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

Options:
  --experiments TEXT             Experiment names or IDs (comma delimited).
                                 For example, 'sklearn_wine,sklearn_iris' or
                                 '1,2'. 'all' will export all experiments.
                                 [required]
  --output-dir TEXT              Output directory.  [required]
  --export-permissions BOOLEAN   Export Databricks permissions.  [default:
                                 False]
  --run-start-time TEXT          Only export runs started after this UTC time
                                 (inclusive). Format: YYYY-MM-DD.
  --runs-until TEXT                   Only export runs started before this UTC time
                                 (exclusive). Use with --run-start-time to
                                 define a time window. Format: YYYY-MM-DD.
  --export-deleted-runs BOOLEAN  Export deleted runs.  [default: False]
  --notebook-formats TEXT        Databricks notebook formats. Values are
                                 SOURCE, HTML, JUPYTER or DBC (comma
                                 seperated).
  --use-threads BOOLEAN          Process in parallel using threads.  [default:
                                 False]
```

#### Examples

##### Export experiments by experiment ID
```
export-experiments \
  --experiments 1280664374380606,e090757fcb8f49cb \
  --output-dir out
```

##### Export experiments by experiment name
```
export-experiments \
  --experiments /Users/me@my.com/sklearn_iris,/Users/me@my.com/keras_mnist \
  --output-dir out
```

##### Export experiments from filename 
```
export-experiments \
  --output-dir out \
  --experiments my-experiments.txt
```

where `my-experiments.txt` is:
```
/Users/me@my.com/sklearn_iris
/Users/me@my.com/keras_mnist
```

##### Export all experiments
```
export-experiments \
  --experiments all --output-dir out
```

```
Exporting experiment: {'name': '/Users/me@my.com/sklearn_iris', 'id': '1280664374380606', 'mlflow.experimentType': 'MLFLOW_EXPERIMENT', 'lifecycle_stage': 'active'}
Exporting experiment: {'name': '/Users/me@my.com/keras_mnist', 'id': 'e090757fcb8f49cb', 'mlflow.experimentType': 'NOTEBOOK', 'lifecycle_stage': 'active'}
. . .
249 experiments exported
1770/1770 runs succesfully exported
Duration: 103.6 seonds
```

##### Export experiments with time window (daily/monthly)
```
export-experiments \
  --experiments sklearn_wine,keras_mnist \
  --output-dir out \
  --run-start-time 2024-01-01 \
  --runs-until 2024-04-01
```

This exports only runs from specified experiments that started between 2024-01-01 (inclusive) and 2024-04-01 (exclusive), allowing for incremental migrations in time-bounded chunks.

##### Export experiments with time window (hourly chunks)
```
# Export first 4 hours of a specific day
export-experiments \
  --experiments all \
  --output-dir out/2024-01-01_00-04 \
  --run-start-time "2024-01-01 00:00:00" \
  --runs-until "2024-01-01 04:00:00"

# Export next 4 hours
export-experiments \
  --experiments all \
  --output-dir out/2024-01-01_04-08 \
  --run-start-time "2024-01-01 04:00:00" \
  --runs-until "2024-01-01 08:00:00"
```

This allows very granular control for large tracking servers, enabling exports in small time chunks (hours or even minutes).

### Import experiments

Import experiments from a directory. Reads the manifest file to import expirements and their runs.

The experiment will be created if it does not exist in the destination tracking server. 
If the experiment already exists, the source runs will be added to it.


#### Usage

```
import-experiments --help

Options:
  --input-dir TEXT               Input directory.  [required]
  --import-permissions BOOLEAN   Import Databricks permissions using the HTTP
                                 PATCH method.  [default: False]
  --import-source-tags BOOLEAN   Import source information for registered
                                 model and its versions ad tags in destination
                                 object.  [default: False]
  --use-src-user-id BOOLEAN      Set the destination user field to the source
                                 user field.  Only valid for open source
                                 MLflow.  When importing into Databricks, the
                                 source user field is ignored since it is
                                 automatically picked up from your Databricks
                                 access token.  There is no MLflow API
                                 endpoint to explicity set the user_id for Run
                                 and Registered Model.  [default: False]
  --experiment-rename-file TEXT  File with experiment names replacements:
                                 comma-delimited line such as
                                 'old_name,new_name'.
  --use-threads BOOLEAN          Process in parallel using threads.  [default:
                                 False]
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


### Export Logged Models

Export several (or all) logged models to a directory.

#### Usage
```
export-logged-models --help

Options:
  --experiment-ids TEXT  List of experiment IDs (comma delimited).  [required]
  --output-dir TEXT      Output directory.  [required]
```

#### Examples 

##### Export logged models for specific experiment ids
```
 export-logged-models \
    --experiment-ids '0,1' --output-dir out
```

##### Export all logged models
```
 export-logged-models \
    --experiment-ids all --output-dir out
```

### Import Logged Models
Import logged models from a directory. Reads the manifest file to import logged models under the experiment.

#### Usage

```
export-logged-models --help

Options:
  --experiment-ids TEXT  List of experiment IDs (comma delimited).
                         For example, '1,2'. 'all' will export all logged
                         model from all experiments.  [required]
  --output-dir TEXT      Output directory.  [required]
  --help                 Show this message and exit.
```

#### Example

```
import-logged-models \ 
    --input-dir exported_logged_models
```
### Export Traces

Export several (or all) traces to a directory.

#### Usage

```
export-traces --help 

Options:
  --experiment-ids TEXT  List of experiment IDs (comma delimited).
                         For example, '1,2'. 'all' will export all logged
                         model from all experiments.  [required]
  --output-dir TEXT      Output directory.  [required]
  --help                 Show this message and exit.
```

#### Examples 

##### Export traces for specific experiment ids
```
 export-traces \
    --experiment-ids '0,1' --output-dir out
```

##### Export all traces
```
 export-traces \
    --experiment-ids all --output-dir out
```

### Import Traces
Import traces from a directory. Reads the manifest file to import traces under the experiment.

#### Usage

```
import-traces --help

Options:
  --input-dir TEXT  Input directory.  [required]
  --help            Show this message and exit.
```

#### Example

```
import-traces \
    --input-dir exported_traces
```


 
## Prompts
 
Export/import prompts from the MLflow Prompt Registry (MLflow 2.21.0+).
 
**Notes:** 
* Prompt Registry support requires MLflow 2.21.0 or higher. The export/import will be skipped with a warning message if the MLflow version doesn't support prompts.
* **Version handling**: MLflow 3.0+ uses efficient pagination to export all prompt versions. MLflow 2.21-2.x uses iterative discovery with early stopping (stops after 3 consecutive missing versions).
 
### Export prompts
 
Export prompts from the MLflow Prompt Registry to a directory.
 
Source: [export_prompts.py](mlflow_export_import/bulk/export_prompts.py).
 
#### Usage
 
```
export-prompts --help
 
Options:
  --output-dir TEXT        Output directory.  [required]
  --prompts TEXT           Prompt names: 'all' for all prompts, comma-delimited
                          list (e.g., 'prompt1,prompt2'), or file path ending
                          with '.txt' containing prompt names (one per line).
                          [required]
  --use-threads BOOLEAN    Use multithreading for export.  [default: False]
```
 
#### Examples
 
##### Export all prompts
```
export-prompts \
  --output-dir out/prompts \
  --prompts all
```
 
##### Export specific prompts
```
export-prompts \
  --output-dir out/prompts \
  --prompts my-prompt-1,my-prompt-2
```

##### Export prompts from filename
```
export-prompts \
  --output-dir out/prompts \
  --prompts my-prompts.txt
```

where `my-prompts.txt` is:
```
my-prompt-1
my-prompt-2
```
 
### Import prompts
 
Import prompts to the MLflow Prompt Registry from a directory.
 
Source: [import_prompts.py](mlflow_export_import/bulk/import_prompts.py).
 
#### Usage
 
```
import-prompts --help
 
Options:
  --input-dir TEXT         Input directory containing exported prompts.  [required]
  --delete-prompt BOOLEAN  Delete existing prompt before importing.  [default: False]
  --use-threads BOOLEAN    Use multithreading for import.  [default: False]
```
 
#### Examples
 
```
import-prompts --input-dir out/prompts
```
 
**Notes:** 
* Prompts are imported with their original names and version numbers are preserved.
* All versions of each prompt are exported and imported to maintain complete version history.
* If a prompt with the same name already exists, it will be skipped with a warning to preserve version numbers. Use `--delete-prompt True` to replace existing prompts.


## Evaluation Datasets

Export/import GenAI evaluation datasets from the MLflow tracking server (MLflow 3.4.0+).

**Note:** Evaluation dataset support requires MLflow 3.4.0 or higher and a SQL-based tracking backend (SQLite, PostgreSQL, MySQL). FileStore is not supported. The export/import will be skipped with a warning message if the MLflow version doesn't support evaluation datasets or if using FileStore.

### Export evaluation datasets

Export evaluation datasets to a directory.

Source: [export_evaluation_datasets.py](mlflow_export_import/bulk/export_evaluation_datasets.py).

#### Usage

```
export-evaluation-datasets --help

Options:
  --output-dir TEXT              Output directory.  [required]
  --evaluation-datasets TEXT     Evaluation dataset names: 'all' for all datasets, 
                                comma-delimited list (e.g., 'dataset1,dataset2'), 
                                or file path ending with '.txt' containing dataset 
                                names (one per line).  [required]
  --experiment-ids TEXT    Comma-separated list of experiment IDs to filter
                          datasets. Only used when --evaluation-datasets is 'all'.
  --use-threads BOOLEAN    Use multithreading for export.  [default: False]
```

#### Examples

##### Export all evaluation datasets
```
export-evaluation-datasets \
  --output-dir out/evaluation_datasets \
  --evaluation-datasets all
```

##### Export specific evaluation datasets
```
export-evaluation-datasets \
  --output-dir out/evaluation_datasets \
  --evaluation-datasets wine-quality-eval,iris-classification-eval
```

##### Export all evaluation datasets for specific experiments
```
export-evaluation-datasets \
  --output-dir out/evaluation_datasets \
  --evaluation-datasets all \
  --experiment-ids 1,2,3
```

**Note:** `--experiment-ids` only filters when `--evaluation-datasets` is set to 'all'. If you specify specific dataset names, `--experiment-ids` is ignored.

### Import evaluation datasets

Import evaluation datasets from a directory.

Source: [import_evaluation_datasets.py](mlflow_export_import/bulk/import_evaluation_datasets.py).

#### Usage

```
import-evaluation-datasets --help

Options:
  --input-dir TEXT                      Input directory containing exported evaluation datasets.  [required]
  --delete-evaluation-dataset BOOLEAN   Delete existing evaluation dataset before importing.  [default: False]
  --use-threads BOOLEAN                 Use multithreading for import.  [default: False]
```

#### Examples

##### Import evaluation datasets
```
import-evaluation-datasets --input-dir out/evaluation_datasets
```

##### Import with evaluation dataset deletion (if dataset exists, delete it first)
```
import-evaluation-datasets \
  --input-dir out/evaluation_datasets \
  --delete-evaluation-dataset True
```

**Note:** If an evaluation dataset with the same name already exists, it will be skipped with a warning. Use `--delete-evaluation-dataset True` to replace existing datasets.
