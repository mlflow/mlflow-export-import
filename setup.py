
from setuptools import setup, find_packages
  
setup(name="mlflow_export_import",
      version="1.0.0",
      author="Andre M",
      description="MLflow Export/Import experiments, runs or models",
      url="https://github.com/amesar/mlflow-export-import",
      python_requires=">=3.7",
      packages=find_packages(),
      zip_safe=False,
      install_requires=[
          "mlflow>=1.11.0",
          "pytest==5.3.5",
          "wheel"
      ])
