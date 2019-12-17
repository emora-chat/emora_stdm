
class Step:

    def __init__(self, node, source=None, label=None, **kwargs):
        self.node = node
        self.source = source
        self.label = label
        self.__dict__.update(kwargs)

    def __str__(self):
        return 'Step(' + str(self.__dict__) + ')'

