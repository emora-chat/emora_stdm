
class Settings(dict):

    def __init__(self, **kwargs):
        dict.__init__(kwargs)

    def update(self, **kwargs):
        for k, v in kwargs.items():
            self[k] = v

    def __getattr__(self, item):
        return self._dictionary[item]

    def __setattr__(self, key, value):
        self._dictionary[key] = value

    def __str__(self):
        return 'Settings(' + ', '.join([k + '=' + str(v) for k, v in self.items()]) + ')'

    def __repr__(self):
        return str(self)
