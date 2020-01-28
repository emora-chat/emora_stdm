
class Settings(dict):

    def __init__(self, **kwargs):
        dict.__init__(self, kwargs)

    def update(self, **kwargs):
        for k, v in kwargs.items():
            self[k] = v

    def __getattr__(self, item):
        return dict.__getitem__(self, item)

    def __setattr__(self, key, value):
        dict.__setitem__(self, key, value)

    def __str__(self):
        return 'Settings(' + ', '.join([k + '=' + str(v) for k, v in self.items()]) + ')'

    def __repr__(self):
        return str(self)
