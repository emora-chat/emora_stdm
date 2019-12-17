

class DefaultDictionary(dict):

    def __init__(self, default=None):
        dict.__init__(self)
        self._default = default

    def set_default(self, function):
        self._default = function

    def __getitem__(self, item):
        if self._default is None or item in self:
            return dict.__getitem__(self, item)
        else:
            return self._default(item)

