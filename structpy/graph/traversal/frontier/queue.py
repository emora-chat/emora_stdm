
from structpy.graph.traversal.frontier.frontier import Frontier
from structpy import I
from collections import deque

class Queue(Frontier, deque):

    def __init__(self):
        deque.__init__(self)

    add = deque.appendleft

    get = deque.pop

    def __str__(self):
        return 'FrontierQueue(' + ', '.join([str(x) for x in
                I(self, __iter__=(lambda self: deque.__iter__(self)))]) + ')'

    def __repr__(self):
        return str(self)
