
class Pointer:

    def __init__(self, value=None):
        self.ptr_value = value

    def set_ptr(self, value):
        self.ptr_value = value
        return self

    def __imul__(self, other):
        self.ptr_value = other
        return self

    def __pos__(self):
        return self.ptr_value

    def __str__(self):
        return '<Pointer: ' + str(self.ptr_value) + '>'

    def __repr__(self):
        return '<Pointer: ' + repr(self.ptr_value) + '>'


_metaClasses = {}

def PointerItem(item):

    if item.__class__ in _metaClasses:
        return _metaClasses[item.__class__](item)
    else:

        class _PointerItem(Pointer, item.__class__):
            def __getattribute__(self, e):
                if e in {'__str__', '__class__', '__repr__', '__imul__', '__pos__', 'set_ptr', 'ptr_value'}:
                    return Pointer.__getattribute__(self, e)
                return Pointer.__getattribute__(self, 'ptr_value').__getattribute__(e)

        _metaClasses[item.__class__] = _PointerItem
        return _PointerItem(item)


