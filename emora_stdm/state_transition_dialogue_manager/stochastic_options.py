
import random


def StochasticOptions(iterable):
    if isinstance(iterable, dict):
        return WeightedStochasticOptions(iterable)
    else:
        return UniformStochasticOptions(iterable)


class UniformStochasticOptions(set):

    def __init__(self, iterable):
        set.__init__(self, iterable)

    def select(self):
        options = list(self)
        assert len(options) > 0
        return random.choice(options)


class WeightedStochasticOptions(dict):

    def __init__(self, dict_like):
        dict.__init__(dict_like)

    def select(self):
        options = list(self.keys())
        assert len(options) > 0
        total = sum(self.values())
        if total <= 0.0:
            return random.choice(options)
        thresholds = []
        curr = 0
        for t in options:
            prob = self[t] / total
            curr += prob
            thresholds.append(curr)
        r = random.uniform(0, 1.0)
        for i, threshold in enumerate(thresholds):
            if r < threshold:
                return options[i]
        return options[-1]
