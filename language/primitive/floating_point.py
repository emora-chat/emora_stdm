
class Float:

    def __init__(self, value=0.0):
        self._value = float(value)

    def value(self):
        return self._value

    def set_value(self, value):
        self._value = value

    def __add__(self, other):
        return self._value + float(other)

    def __sub__(self, other):
        return self._value - float(other)

    def __mul__(self, other):
        return self._value * float(other)

    def __truediv__(self, other):
        return self._value // float(other)

    def __iadd__(self, other):
        self._value += float(other)
        return self

    def __isub__(self, other):
        self._value -= float(other)
        return self

    def __imul__(self, other):
        self._value *= float(other)
        return self

    def __idiv__(self, other):
        self._value /= float(other)
        return self

    def __eq__(self, other):
        return self._value == float(other)

    def __ne__(self, other):
        return self._value != float(other)

    def __gt__(self, other):
        return self._value > float(other)

    def __lt__(self, other):
        return self._value < float(other)

    def __ge__(self, other):
        return self._value >= float(other)

    def __le__(self, other):
        return self._value <= float(other)

    def __float__(self):
        return self._value

    def __int__(self):
        return int(self._value)

    def __hash__(self):
        return hash(self._value)

    def __str__(self):
        return str(self._value)

    def __repr__(self):
        return repr(self._value)