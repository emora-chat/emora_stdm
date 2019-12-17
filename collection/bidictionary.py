
from structpy.language import I

class Bidictionary:

    @staticmethod
    def _create_reverse(bidict):
        reverse = Bidictionary()
        reverse._forward = bidict._backward
        reverse._backward = bidict._forward
        return reverse

    def __init__(self, other=None):
        self._forward = {}
        self._backward = {}
        if other is not None:
            for k, v in other.items():
                self[k] = v

    def forward(self):
        return self._forward

    def backward(self):
        return self._backward

    def reverse(self):
        return Bidictionary._create_reverse(self)

    def keys(self):
        return self._forward.keys()

    def values(self):
        return self._backward.keys()

    def items(self):
        return self._forward.items()

    def __iter__(self):
        return self._forward.__iter__()

    def __getitem__(self, item):
        return self._forward[item]

    def __setitem__(self, key, value):
        self._forward.__setitem__(key, value)
        self._backward.__setitem__(value, key)

    def __delitem__(self, key):
        self._backward.__delitem__(self[key])
        self._forward.__delitem__(key)

    def __len__(self):
        return len(self._forward)

