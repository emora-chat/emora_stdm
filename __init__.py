
import os
print('STDM', os.getcwd())

import structpy
import StateTransitionDialogueManager.src.expression as expression
import StateTransitionDialogueManager.src.knowledge_base as knowledge_base
import StateTransitionDialogueManager.src.dialogue_flow as dialogue_flow
from StateTransitionDialogueManager.modules.holiday import component as holiday
from StateTransitionDialogueManager.modules.opening import component as opening
from StateTransitionDialogueManager.modules.general_greet import component as general_greet
