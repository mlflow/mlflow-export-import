from setuptools import setup, find_packages

CORE_REQUIREMENTS = [
    "mlflow-skinny[databricks]",
    "databricks-cli==0.18.0",
    "pandas>=1.5.2",
    "tabulate==0.9.0",
    "wheel"
]


import os
from importlib.machinery import SourceFileLoader
version = (
    SourceFileLoader("mlflow_export_import.version", os.path.join("mlflow_export_import", "version.py")).load_module().__version__
)

setup(
    name="mlflow_export_import",
    version=version,
    author = "Andre Mesarovic",
    description = "Copy MLflow objects (experiments, runs or registered models) to another tracking server",
    long_description=open("README.md").read(),
    long_description_content_type='text/markdown',
    url = "https://github.com/mlflow/mlflow-export-import",
    project_urls={
        "Bug Tracker": "https://github.com/mlflow/mlflow-export-import/issues",
        "Documentation": "https://github.com/mlflow/mlflow-export-import/blob/master/README.md",
        "Source Code": "https://github.com/mlflow/mlflow-export-import/"
    },
    python_requires = ">=3.8",
    packages=find_packages(exclude=["tests", "tests.*"]),
    zip_safe = False,
    install_requires = CORE_REQUIREMENTS,
    extras_require= { "tests": [ "mlflow[databricks]>=2.9.2", "pytest","pytest-html>=3.2.0", "shortuuid>=1.0.11" ] },
    license = "Apache License 2.0",
    keywords = "mlflow ml ai",
    classifiers = [
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent"
    ],
    entry_points = {
        "console_scripts": [
            "export-all = mlflow_export_import.bulk.export_all:main",
            "import-all = mlflow_export_import.bulk.import_models:main",
            "export-models = mlflow_export_import.bulk.export_models:main",
            "import-models = mlflow_export_import.bulk.import_models:main",
            "export-run = mlflow_export_import.run.export_run:main",
            "import-run = mlflow_export_import.run.import_run:main",
            "export-experiment = mlflow_export_import.experiment.export_experiment:main",
            "import-experiment = mlflow_export_import.experiment.import_experiment:main",
            "export-experiments = mlflow_export_import.bulk.export_experiments:main",
            "import-experiments = mlflow_export_import.bulk.import_experiments:main",
            "export-model = mlflow_export_import.model.export_model:main",
            "import-model = mlflow_export_import.model.import_model:main",
            "export-model-version = mlflow_export_import.model_version.export_model_version:main",
            "import-model-version = mlflow_export_import.model_version.import_model_version:main",
            "download-notebook = mlflow_export_import.notebook.download_notebook:main",
            "copy-model-version = mlflow_export_import.copy.copy_model_version:main",
            "copy-run = mlflow_export_import.copy.copy_run:main",
            "get-model-signature = mlflow_export_import.tools.get_model_signature:main",
            "set-model-signature = mlflow_export_import.tools.set_model_signature:main",
            "list-model-versions-without-signatures = mlflow_export_import.tools.list_model_versions_without_signatures:main",
            "http-client = mlflow_export_import.client.http_client:main"
         ]
      }
)
