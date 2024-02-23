class Configs:
    EXPORT_START_DATE = '2024-02-18' # Can't be empty
    EXPORT_END_DATE = '2024-02-20'   # Can't empty
    APPLY_EXPORT_FILTER = True
    SKIP_EXPORT_IF_EXISTS = True
    EXPORT_MODEL_NAMES = []; 

    def __init__(self):
      pass;
        
Config = Configs();