
from enum import Enum


class State(str):

    def __eq__(self, other):
        if isinstance(other, Enum):
            return str.__eq__(self, str(other))
        else:
            return str.__eq__(self, other)

    def __hash__(self):
        return str.__hash__(self)

