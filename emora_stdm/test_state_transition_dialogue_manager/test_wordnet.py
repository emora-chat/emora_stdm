
import pytest
from emora_stdm.state_transition_dialogue_manager.wordnet import synonyms, hyponyms


def test_synonyms():
    child_syns = synonyms('child')
    assert 'kid' in child_syns
    assert 'minor' in child_syns
    car_syns = synonyms('car')
    assert 'automobile' in car_syns

def test_hyponyms():
    vehicle_hypos = hyponyms('car')
    assert 'car' in vehicle_hypos
    assert 'sedan' in vehicle_hypos
