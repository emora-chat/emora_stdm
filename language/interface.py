
from types import MethodType
from functools import partial

def interface(**interface_functions):
    return partial(I, **interface_functions)

def CreateInterface(obj, **interface_functions):
    """
    in progress...
    """

    class Interface(obj.__class__):

        def __init__(self, obj):
            self._data_object = obj

        def __getattr__(self, item):
            return self._data_object.__getattribute__(item)

    i = Interface(obj)
    for function_name, function_value in interface_functions.items():
        if not hasattr(function_value, '__self__'):
            interface_functions[function_name] = MethodType(function_value, i)
    i.__dict__.update(interface_functions)
    return i

class I:
    """
    wrapper class to add interface functions to an object

    requirements of use code:
    - cannot use object comparator 'is' (since wrapper object is located differently in memory)
    """

    def __init__(self, obj, **interface_functions):
        self._data_object = obj
        for function_name, function_value in interface_functions.items():
            if not hasattr(function_value, '__self__'):
                interface_functions[function_name] = MethodType(function_value, self)
        self.__dict__.update(interface_functions)

    def __getattr__(self, item):
        return self._data_object.__getattribute__(item)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    ######################################################

    def __del__(self):
        try:
            return self._data_object.__del__()
        except AttributeError:
            return

    def __pos__(self):
        try:
            return self._data_object.__pos__()
        except AttributeError:
            return

    def __neg__(self):
        try:
            return self._data_object.__neg__()
        except AttributeError:
            return

    def __abs__(self):
        try:
            return self._data_object.__abs__()
        except AttributeError:
            return

    def __invert__(self):
        try:
            return self._data_object.__invert__()
        except AttributeError:
            return

    def __floor__(self):
        try:
            return self._data_object.__floor__()
        except AttributeError:
            return

    def __ceil__(self):
        try:
            return self._data_object.__ceil__()
        except AttributeError:
            return

    def __trunc__(self):
        try:
            return self._data_object.__trunc__()
        except AttributeError:
            return

    def __int__(self):
        try:
            return self._data_object.__int__()
        except AttributeError:
            return

    def __long__(self):
        try:
            return self._data_object.__long__()
        except AttributeError:
            return

    def __float__(self):
        try:
            return self._data_object.__float__()
        except AttributeError:
            return

    def __complex__(self):
        try:
            return self._data_object.__complex__()
        except AttributeError:
            return

    def __oct__(self):
        try:
            return self._data_object.__oct__()
        except AttributeError:
            return

    def __hex__(self):
        try:
            return self._data_object.__hex__()
        except AttributeError:
            return

    def __index__(self):
        try:
            return self._data_object.__index__()
        except AttributeError:
            return

    def __str__(self):
        try:
            return self._data_object.__str__()
        except AttributeError:
            return

    def __repr__(self):
        try:
            return self._data_object.__repr__()
        except AttributeError:
            return

    def __unicode__(self):
        try:
            return self._data_object.__unicode__()
        except AttributeError:
            return

    def __hash__(self):
        try:
            return self._data_object.__hash__()
        except AttributeError:
            return

    def __bool__(self):
        try:
            return self._data_object.__bool__()
        except AttributeError:
            return

    def __dir__(self):
        try:
            return self._data_object.__dir__()
        except AttributeError:
            return

    def __sizeof__(self):
        try:
            return self._data_object.__sizeof__()
        except AttributeError:
            return

    def __len__(self):
        try:
            return self._data_object.__len__()
        except AttributeError:
            return

    def __iter__(self):
        try:
            return self._data_object.__iter__()
        except AttributeError:
            return

    def __reversed__(self):
        try:
            return self._data_object.__reversed__()
        except AttributeError:
            return

    def __copy__(self):
        try:
            return self._data_object.__copy__()
        except AttributeError:
            return

    def __getinitargs__(self):
        try:
            return self._data_object.__getinitargs__()
        except AttributeError:
            return

    def __getnewargs__(self):
        try:
            return self._data_object.__getnewargs__()
        except AttributeError:
            return

    def __getstate__(self):
        try:
            return self._data_object.__getstate__()
        except AttributeError:
            return

    def __setstate__(self):
        try:
            return self._data_object.__setstate__()
        except AttributeError:
            return

    def __reduce__(self):
        try:
            return self._data_object.__reduce__()
        except AttributeError:
            return

    def __ne__(self, arg0):
        try:
            return self._data_object.__ne__(arg0)
        except AttributeError:
            return

    def __gt__(self, arg0):
        try:
            return self._data_object.__gt__(arg0)
        except AttributeError:
            return

    def __lt__(self, arg0):
        try:
            return self._data_object.__lt__(arg0)
        except AttributeError:
            return

    def __ge__(self, arg0):
        try:
            return self._data_object.__ge__(arg0)
        except AttributeError:
            return

    def __le__(self, arg0):
        try:
            return self._data_object.__le__(arg0)
        except AttributeError:
            return

    def __round__(self, arg0):
        try:
            return self._data_object.__round__(arg0)
        except AttributeError:
            return

    def __add__(self, arg0):
        try:
            return self._data_object.__add__(arg0)
        except AttributeError:
            return

    def __sub__(self, arg0):
        try:
            return self._data_object.__sub__(arg0)
        except AttributeError:
            return

    def __mul__(self, arg0):
        try:
            return self._data_object.__mul__(arg0)
        except AttributeError:
            return

    def __floordiv__(self, arg0):
        try:
            return self._data_object.__floordiv__(arg0)
        except AttributeError:
            return

    def __div__(self, arg0):
        try:
            return self._data_object.__div__(arg0)
        except AttributeError:
            return

    def __truediv__(self, arg0):
        try:
            return self._data_object.__truediv__(arg0)
        except AttributeError:
            return

    def __mod__(self, arg0):
        try:
            return self._data_object.__mod__(arg0)
        except AttributeError:
            return

    def __divmod__(self, arg0):
        try:
            return self._data_object.__divmod__(arg0)
        except AttributeError:
            return

    def __pow__(self, arg0):
        try:
            return self._data_object.__pow__(arg0)
        except AttributeError:
            return

    def __lshift__(self, arg0):
        try:
            return self._data_object.__lshift__(arg0)
        except AttributeError:
            return

    def __rshift__(self, arg0):
        try:
            return self._data_object.__rshift__(arg0)
        except AttributeError:
            return

    def __and__(self, arg0):
        try:
            return self._data_object.__and__(arg0)
        except AttributeError:
            return

    def __or__(self, arg0):
        try:
            return self._data_object.__or__(arg0)
        except AttributeError:
            return

    def __xor__(self, arg0):
        try:
            return self._data_object.__xor__(arg0)
        except AttributeError:
            return

    def __radd__(self, arg0):
        try:
            return self._data_object.__radd__(arg0)
        except AttributeError:
            return

    def __rsub__(self, arg0):
        try:
            return self._data_object.__rsub__(arg0)
        except AttributeError:
            return

    def __rmul__(self, arg0):
        try:
            return self._data_object.__rmul__(arg0)
        except AttributeError:
            return

    def __rfloordiv__(self, arg0):
        try:
            return self._data_object.__rfloordiv__(arg0)
        except AttributeError:
            return

    def __rdiv__(self, arg0):
        try:
            return self._data_object.__rdiv__(arg0)
        except AttributeError:
            return

    def __rtruediv__(self, arg0):
        try:
            return self._data_object.__rtruediv__(arg0)
        except AttributeError:
            return

    def __rmod__(self, arg0):
        try:
            return self._data_object.__rmod__(arg0)
        except AttributeError:
            return

    def __rdivmod__(self, arg0):
        try:
            return self._data_object.__rdivmod__(arg0)
        except AttributeError:
            return

    def __rpow__(self, arg0):
        try:
            return self._data_object.__rpow__(arg0)
        except AttributeError:
            return

    def __rlshift__(self, arg0):
        try:
            return self._data_object.__rlshift__(arg0)
        except AttributeError:
            return

    def __rrshift__(self, arg0):
        try:
            return self._data_object.__rrshift__(arg0)
        except AttributeError:
            return

    def __rand__(self, arg0):
        try:
            return self._data_object.__rand__(arg0)
        except AttributeError:
            return

    def __ror__(self, arg0):
        try:
            return self._data_object.__ror__(arg0)
        except AttributeError:
            return

    def __rxor__(self, arg0):
        try:
            return self._data_object.__rxor__(arg0)
        except AttributeError:
            return

    def __iadd__(self, arg0):
        try:
            return self._data_object.__iadd__(arg0)
        except AttributeError:
            return

    def __isub__(self, arg0):
        try:
            return self._data_object.__isub__(arg0)
        except AttributeError:
            return

    def __imul__(self, arg0):
        try:
            return self._data_object.__imul__(arg0)
        except AttributeError:
            return

    def __ifloordiv__(self, arg0):
        try:
            return self._data_object.__ifloordiv__(arg0)
        except AttributeError:
            return

    def __idiv__(self, arg0):
        try:
            return self._data_object.__idiv__(arg0)
        except AttributeError:
            return

    def __itruediv__(self, arg0):
        try:
            return self._data_object.__itruediv__(arg0)
        except AttributeError:
            return

    def __imod__(self, arg0):
        try:
            return self._data_object.__imod__(arg0)
        except AttributeError:
            return

    def __ipow__(self, arg0):
        try:
            return self._data_object.__ipow__(arg0)
        except AttributeError:
            return

    def __ilshift__(self, arg0):
        try:
            return self._data_object.__ilshift__(arg0)
        except AttributeError:
            return

    def __irshift__(self, arg0):
        try:
            return self._data_object.__irshift__(arg0)
        except AttributeError:
            return

    def __iand__(self, arg0):
        try:
            return self._data_object.__iand__(arg0)
        except AttributeError:
            return

    def __ior__(self, arg0):
        try:
            return self._data_object.__ior__(arg0)
        except AttributeError:
            return

    def __ixor__(self, arg0):
        try:
            return self._data_object.__ixor__(arg0)
        except AttributeError:
            return

    def __format__(self, arg0):
        try:
            return self._data_object.__format__(arg0)
        except AttributeError:
            return

    def __getitem__(self, arg0):
        try:
            return self._data_object.__getitem__(arg0)
        except AttributeError:
            return

    def __delitem__(self, arg0):
        try:
            return self._data_object.__delitem__(arg0)
        except AttributeError:
            return

    def __contains__(self, arg0):
        try:
            return self._data_object.__contains__(arg0)
        except AttributeError:
            return

    def __missing__(self, arg0):
        try:
            return self._data_object.__missing__(arg0)
        except AttributeError:
            return

    def __instancecheck__(self, arg0):
        try:
            return self._data_object.__instancecheck__(arg0)
        except AttributeError:
            return

    def __subclasscheck__(self, arg0):
        try:
            return self._data_object.__subclasscheck__(arg0)
        except AttributeError:
            return

    def __deepcopy__(self, arg0):
        try:
            return self._data_object.__deepcopy__(arg0)
        except AttributeError:
            return

    def __setitem__(self, arg0, arg1):
        try:
            return self._data_object.__setitem__(arg0, arg1)
        except AttributeError:
            return

    def __call__(self, arg0, arg1):
        try:
            return self._data_object.__call__(arg0, arg1)
        except AttributeError:
            return


    '''
    mms0 = 'del pos neg abs invert floor ceil trunc int long float complex oct hex ' + \
           'index str repr unicode hash bool dir sizeof len iter reversed ' + \
           'copy getinitargs getnewargs getstate setstate reduce'
    mms1 = 'ne gt lt ge le round add sub mul floordiv div truediv mod divmod pow ' + \
           'lshift rshift and or xor radd rsub rmul rfloordiv rdiv rtruediv rmod rdivmod ' + \
           'rpow rlshift rrshift rand ror rxor iadd isub imul ifloordiv idiv itruediv ' + \
           'imod ipow ilshift irshift iand ior ixor format getitem delitem contains ' + \
           'missing instancecheck subclasscheck deepcopy'
    mms2 = 'setitem call'

    mmss = [mms0, mms1, mms2]
    for i in range(len(mmss)):
        mms = mmss[i].split()
        for mm in mms:
            argsstr = ', '.join(['arg' + str(j) for j in range(i)])
            paramstr = argsstr
            if paramstr:
                paramstr = ', ' + paramstr
            print('def __' + mm + '__(self' + paramstr + '):\n' + \
                  '    try:\n' + \
                  '        return self._data_object.__' + mm + '__(' + argsstr + ')\n' + \
                  '    except AttributeError:\n' + \
                  '        return')
    '''
