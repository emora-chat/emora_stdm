
import random


def random_max(collection, key=None):
    max_collection = []
    if key is not None:
        for item in collection:
            if not max_collection or key(item) > key(max_collection[0]):
                max_collection = [item]
            elif key(max_collection[0]) == key(item):
                max_collection.append(item)
    else:
        for item in collection:
            if not max_collection or item > max_collection[0]:
                max_collection = [item]
            elif item == max_collection[0]:
                max_collection.append(item)
    return random.choice(max_collection)

class ConfigurationDict(dict):

    def __hash__(self):
        value = 0
        for e in self:
            value = value ^ hash(e)
        return value

    def __eq__(self, other):
        return dict.__eq__(self, other)


class HashableDict(ConfigurationDict):
    def __init__(self, other=None):
        if other is None:
            other = {}
        ConfigurationDict.__init__(self, other)
        self._altered = set()

    def __setitem__(self, key, value):
        self._altered.add(key)
        ConfigurationDict.__setitem__(self, key, value)

    def update(self, mapping):
        for k, v in mapping.items():
            self[k] = v

    def altered(self):
        return self._altered

    def clear_altered(self):
        self._altered.clear()



class HashableSet(set):
    def __hash__(self):
        value = 0
        for e in self:
            value = value ^ hash(e)
        return value
    def __eq__(self, other):
        return set.__eq__(self, other)

class AlterationTrackingDict(dict):
    def __init__(self, other=None):
        dict.__init__(self, other)
        self._altered = set()
    def __setitem__(self, key, value):
        self._altered.add(key)
        dict.__setitem__(self, key, value)
    def update(self, mapping):
        for k, v in mapping.items():
            self[k] = v
    def altered(self):
        return self._altered
    def clear_altered(self):
        self._altered.clear()