config = {
    "version": 1,
    "formatters": {
      "simple": {
        "format": "%(asctime)s - %(levelname)s - %(message)s",
        "datefmt": "%d-%b-%y %H:%M:%S"
      }
    },
    "handlers": {
      "console": {
        "class": "logging.StreamHandler",
        "level": "DEBUG",
        "formatter": "simple",
        "stream": "ext://sys.stdout"
      },
      "file": {
        "class": "logging.FileHandler",
        "filename": "/tmp/mlflow-export-import.log",
        "level": "INFO",
        "formatter": "simple"
      }
    },
    "loggers": {
      "sampleLogger": {
        "level": "DEBUG",
        "handlers": [
          "console"
        ],
        "propagate": False
      }
    },
    "root": {
      "level": "DEBUG",
      "handlers": [
        "console",
        "file"
      ]
    }
}
