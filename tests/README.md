# Mlflow Export Import - Tests

## Overview

There are two types of tests:
* [Open source MLlflow tests](open_source/README.md). Numerous tests. Launches a source and destination tracking server and runs tests to ensure that the exported MLflow objects (runs, experiments and registered models) are correctly imported.
* [Databricks MLflow notebook tests](databricks_notebooks/README.md). Smaller number of smoke tests for Databricks notebooks. Launches Databricks jobs to ensure that [Databricks export-import notebooks](../databricks_notebooks/README.md) execute properly.

## Setup

```
pip install -e ..[tests] --upgrade 
```

## Reports and logs

The test script creates the folowing files:
* run_tests.log - log of the entire test run.
* run_tests_junit.xml - report for all tests in standard JUnit XML format.
* run_tests_report.html - report for all tests in HTML format.

**Sample reports**

Open Source Tests:
* [run_tests_junit.xml](open_source/samples/run_tests_junit.xml)
* [run_tests_report.html](open_source/samples/run_tests_report.html)

Databricks Tests:
* [run_tests_junit.xml](databricks/samples/run_tests_junit.xml)
* [run_tests_report.html](databricks/samples/run_tests_report.html)

Failed Databricks Tests:
* [run_tests_junit.xml](databricks/samples/failed/run_tests_junit.xml)
* [run_tests_report.html](databricks/samples/failed/run_tests_report.html)


