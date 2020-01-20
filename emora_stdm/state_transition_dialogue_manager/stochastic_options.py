
import random


def StochasticOptions(iterable):
    if isinstance(iterable, dict):
        raise NotImplementedError('weighted stochastic options not implemented') # todo
    else:
        return UniformStochasticOptions(iterable)

class UniformStochasticOptions(set):

    def __init__(self, iterable):
        set.__init__(self, iterable)

    def select(self):
        return random.choice(list(self))

