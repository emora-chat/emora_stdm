
import pytest
from emora_stdm import UpdateRules

def IF(ngrams, vars, args):
    for arg in args:
        var, val = arg.split('=')
        if var not in vars or vars[var] != val:
            return False
    return True

def SET(ngrams, vars, args):
    for arg in args:
        var, val = arg.split('=')
        vars[var] = val

def test_update_rules():
    vars = {}
    rules = UpdateRules(vars=vars, macros={'IF': IF, 'SET': SET})
    rules.add('[$x={cat, dog, fish, bird}]', '#SET(y=matched)')
    rules.add('#IF(x=cat, y=matched)', '#SET(z=something)')
    rules.add('#IF(z=something)', 'hallelujah (1.0)')
    rules.add('#IF(z=something) (2.0)', '#SET(a=blah) wow (1.0)')
    rules.add('#IF(a=blah)', '#SET(b=blah)')
    result, score = rules.update('i have a cat', debugging=False)
    assert result.generate(vars=vars, macros={'IF': IF, 'SET': SET}).strip() == 'wow'
    assert vars['z'] == 'something'
    assert vars['x'] == 'cat'
    assert 'b' not in vars
