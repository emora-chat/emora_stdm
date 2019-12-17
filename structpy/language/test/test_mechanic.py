
import pytest

from structpy.language.mechanic import Mechanic, MechanicMethod


def test_mechanic():

    @Mechanic(x=0)
    def foo(this, x, y):
        this.x += 1
        return str(this.x) + str(x) + str(y)

    assert foo('a', 'b') == '1ab'
    assert foo('a', 'b') == '2ab'
    assert foo('hello', 'world') == '3helloworld'

def test_mechanic_method():

    class Bar:

        def __init__(self, z):
            self.z = z

        @Mechanic(x=0)
        def foo(this, self, y):
            this.x += 1
            return self.z + this.x + y

    b = Bar(10)
    assert b.foo(5) == 16
    assert b.foo(5) == 17
    assert b.foo(6) == 19

def test_multiple_mechanics():

    class Bar:

        def __init__(self, z):
            self.z = z

            @MechanicMethod(self, x=0)
            def foo(this, self, y):
                this.x += 1
                return self.z + this.x + y

    b1 = Bar(10)
    assert b1.foo(5) == 16

    b2 = Bar(100)
    assert b2.foo(15) == 116
