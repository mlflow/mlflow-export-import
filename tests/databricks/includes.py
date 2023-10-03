class Dict2Class():
    def __init__(self, dct):
        self.dct = dct
        for k,v in dct.items():
            if isinstance(v,dict):
                v = Dict2Class(v)
            setattr(self, k, v)
    def __str__(self):
        return str(self.dct)
