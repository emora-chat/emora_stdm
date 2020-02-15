
from collections import deque


class Memory:

    def __init__(self, n_OR_collection):
        if isinstance(n_OR_collection, int):
            self._data = deque([None] * n_OR_collection)
        else:
            self._data = deque(n_OR_collection)
        self._init_vals = list(self._data)

    def add(self, item):
        self._data.appendleft(item)
        self._data.pop()

    def clear(self):
        self._data = deque(self._init_vals)

    def __contains__(self, item):
        return item in self._data

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return self._data.__iter__()

    def __getitem__(self, item):
        return self._data[item]

    def __setitem__(self, key, value):
        self._data[key] = value

    def __str__(self):
        return 'Memory({})'.format(', '.join(self._data))