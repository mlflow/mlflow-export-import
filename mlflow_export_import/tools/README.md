# MLflow Export Import Tools - Experimental

## Overview

Experimental WIP.

### Filter one model from `export-models` directory

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
