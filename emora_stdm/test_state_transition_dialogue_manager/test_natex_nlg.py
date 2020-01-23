
import pytest
from emora_stdm.state_transition_dialogue_manager.natex_nlg import NatexNLG


def test_generation():
    ng = NatexNLG('this is {a, the} test case')
    ng.generate(debugging=True)