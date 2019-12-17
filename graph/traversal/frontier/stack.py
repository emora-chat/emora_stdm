
from structpy.graph.traversal.frontier.frontier import Frontier

class Stack(Frontier, list):

    def __init__(self, *args, **kwargs):
        list.__init__(self)
        Frontier.__init__(self, *args, **kwargs)

    add = list.append

    get = list.pop

    def __len__(self):
        return list.__len__(self)

    def __str__(self):
        return 'FrontierStack(' + ', '.join([str(x) for x in self]) + ')'
