
from setuptools import setup, find_packages
  
setup(name="mlflow_export_import",
      version="1.0.0",
      author="Andre M",
      description="MLflow export/import experiments, runs or registered models",
      url="https://github.com/amesar/mlflow-export-import",
      python_requires=">=3.7",
      packages=find_packages(),
      zip_safe=False,
      install_requires=[
          "mlflow>=1.15.0",
          "pytest==5.3.5",
          "wheel"
      ],
      entry_points={
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
             "export-model-list = mlflow_export_import.model.export_model_list:main",
             "import-model = mlflow_export_import.model.import_model:main",
             "list-models = mlflow_export_import.model.list_registered_models:main",
             "http-client = mlflow_export_import.common.http_client:main"
         ]
      },
)
