FROM python:3.10-slim-buster

RUN apt-get update && apt-get install -y

RUN pip install --upgrade pip
RUN pip install 'mlflow==2.14.2' \
                'azureml-mlflow==1.56.0' \
                'python-dotenv==1.0.1' \
                'ipykernel==6.29.5'