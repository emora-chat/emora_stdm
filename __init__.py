import os
cwd = os.getcwd()

from emora_stdm.stdm.StateTransitionDialogueManager.expression import _ExpressionReducer, _expression_parser
from emora_stdm.stdm.StateTransitionDialogueManager.utilities import all_grams, random_choice

from emora_stdm.stdm.StateTransitionDialogueManager.knowledge_base import KnowledgeBase
from emora_stdm.stdm.StateTransitionDialogueManager.utilities import all_grams, random_choice
from emora_stdm.stdm.StateTransitionDialogueManager.dialogue_transition import DialogueTransition
from emora_stdm.stdm.StateTransitionDialogueManager.stdm_exceptions import MissingStateException,\
    MissingOntologyException, MissingKnowledgeException, MissingErrorStateException

from emora_stdm.stdm.StateTransitionDialogueManager.dialogue_flow import DialogueFlow

if 'test_state_machine_dialogue' not in cwd and '/deploy/' in cwd:
    from emora_stdm.stdm.modules.holiday import component as holiday
    from emora_stdm.stdm.modules.opening import component as opening