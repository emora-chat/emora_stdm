
from types import MethodType


class Mechanic:

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __call__(self, f, *args, **kwargs):
        def function(*args, **kwargs):
            return f(self, *args, **kwargs)
        return function


class MechanicMethod:

    def __init__(self, obj, **kwargs):
        self.__dict__.update(kwargs)
        self._obj = obj

    def __call__(self, f, *args, **kwargs):
        def function(*args, **kwargs):
            return f(self, *args, **kwargs)
        method = MethodType(function, self._obj)
        setattr(self._obj, f.__name__, method)
        return
