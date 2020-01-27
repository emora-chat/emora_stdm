
class HashableDict(dict):
    def __hash__(self):
        return id(self)

