from collections import defaultdict


class Multibidict:

    @staticmethod
    def _create_reverse(bidict):
        reverse = Multibidict()
        reverse._forward = bidict._backward
        reverse._backward = bidict._forward
        return reverse

    def __init__(self, other=None):
        self._forward = defaultdict(set)
        self._backward = defaultdict(set)
        if other is not None:
            for k, vs in other.items():
                for v in vs:
                    self[k] = v

    def forward(self):
        return self._forward

    def backward(self):
        return self._backward

    def reverse(self):
        return Multibidict._create_reverse(self)

    def keys(self):
        return self._forward.keys()

    def values(self):
        return self._backward.keys()

    def items(self):
        return self._forward.items()

    def remove(self, key, value):
        self._forward[key].remove(value)
        if len(self._forward[key]) == 0:
            del self._forward[key]
        self._backward[value].remove(key)
        if len(self._backward[value]) == 0:
            del self._backward[value]

    def __iter__(self):
        return self._forward.__iter__()

    def __getitem__(self, item):
        return self._forward[item]

    def __setitem__(self, key, value):
        self._forward[key].add(value)
        self._backward[value].add(key)

    def __delitem__(self, key):
        vals = self._forward[key]
        del self._forward[key]
        for val in vals:
            self._backward[val].remove(key)
            if len(self._backward[val]) == 0:
                del self._backward[val]

    def __len__(self):
        return len(self._forward)

