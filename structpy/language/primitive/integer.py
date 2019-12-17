
class Integer:

    def __init__(self, value=0):
        self._value = int(value)

    def value(self):
        return self._value

    def set_value(self, value):
        self._value = value

    def __add__(self, other):
        return self._value + int(other)

    def __sub__(self, other):
        return self._value - int(other)

    def __mul__(self, other):
        return self._value * int(other)

    def __truediv__(self, other):
        return self._value // int(other)

    def __floordiv__(self, other):
        return self._value // int(other)

    def __iadd__(self, other):
        self._value += int(other)
        return self

    def __isub__(self, other):
        self._value -= int(other)
        return self

    def __imul__(self, other):
        self._value *= int(other)
        return self

    def __idiv__(self, other):
        self._value /= int(other)
        return self

    def __eq__(self, other):
        return self._value == int(other)

    def __ne__(self, other):
        return self._value != int(other)

    def __gt__(self, other):
        return self._value > int(other)

    def __lt__(self, other):
        return self._value < int(other)

    def __ge__(self, other):
        return self._value >= int(other)

    def __le__(self, other):
        return self._value <= int(other)

    def __float__(self):
        return float(self._value)

    def __int__(self):
        return self._value

    def __hash__(self):
        return hash(self._value)

    def __str__(self):
        return str(self._value)

    def __repr__(self):
        return repr(self._value)
