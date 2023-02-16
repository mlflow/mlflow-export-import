# CHANGELOG

## 1.2.0 (2023-02-16)

The 1.2.0 version of MLflow Export Import is a major milestone release.

This release contains an important breaking change from the 1.x API, additional major features and improvements.

Features:

- New streamlined export format for MLflow objects (experiments, runs and registered models)
- Exporting artifacts of a specific version of a model
- Import source system fields and tags
- More Databricks notebook examples: Export_All and Export_Models notebooks
- Added download notebook CLI utility
- Plenty of bug fixes

Breaking Changes:

- [Core] The JSON export file format has been overhauled and made consistent across different MLflow objects. 
1.x export files cannot be read by the 2.x release.

Documentation updates
- Major updates to README files
- Aligned sample JSON files with new format
