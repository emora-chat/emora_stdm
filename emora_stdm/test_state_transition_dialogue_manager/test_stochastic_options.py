
import pytest
from emora_stdm.state_transition_dialogue_manager.stochastic_options import StochasticOptions
from collections import defaultdict

def test_constructor():
    so = StochasticOptions(['a', 'b', 'c'])
    assert so == {'a':1.0, 'b':1.0, 'c':1.0}
    so = StochasticOptions({'a':1.0, 'b':2.0, 'c':1.0})
    assert so == {'a':1.0, 'b':2.0, 'c':1.0}

def test_select():
    so = StochasticOptions({'a':1.0, 'b':2.0, 'c':1.0})
    counter = defaultdict(int)
    n = 10 ** 5
    for i in range(n):
        selection = so.select()
        counter[selection] += 1
    assert counter['a'] == pytest.approx(n / 4, 0.1)
    assert counter['b'] == pytest.approx(n / 2, 0.1)
    assert counter['c'] == pytest.approx(n / 4, 0.1)
