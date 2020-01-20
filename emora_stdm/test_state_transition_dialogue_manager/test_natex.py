
import pytest
from emora_stdm.state_transition_dialogue_manager.natex import Natex

macros = {
    'FOO': (lambda ngrams, vars, assignments, args: {'foo'}),
    'BAR': (lambda ngrams, vars, assignments, args: {'bar', *[x for (x,) in args]} & ngrams)
}

def test_parser():
    natex = r'[this is, {test, eval} {you, me, us}]'
    parser = Natex.Compiler.parser
    print(parser.parse(natex).pretty())

def test_compiler():
    natex = Natex(r'[this is {test, eval} $x=BAR(hello, there, sir) you]')
    natex.compile(ngrams={'hello', 'this is', 'this is hello', 'there'}, macros=macros, debugging=True)
    match = natex.match('this is test ok hello you')
    print('Match:', match)
    print('Var x:', match['x'])


