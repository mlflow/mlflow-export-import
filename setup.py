
from setuptools import setup, find_packages
  
setup(name="mlflow_export_import",
      version="1.0.0",
      author="Andre M",
      description="MLflow export/import experiments, runs or registered models",
      url="https://github.com/amesar/mlflow-export-import",
      python_requires=">=3.7",
      packages=find_packages(),
      zip_safe=False,
      entry_points={
        "mlflow.request_header_provider": "unused=mlflow_export_import.common.usr_agent_header:MlflowExportImportRequestHeaderProvider",
      }    
      install_requires=[
          "mlflow>=1.15.0",
          "pytest==5.3.5",
          "wheel"
      ])
