
import pytest
from emora_stdm.state_transition_dialogue_manager.natex_nlg import NatexNlg


def test_generation():
    ng = NatexNlg('this is {a, the} test case')
    ng.generate(debugging=True)