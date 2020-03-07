
from emora_stdm import DialogueFlow

df = DialogueFlow('root', initial_speaker=DialogueFlow.Speaker.USER)

df.add_user_transition('root', 'initiation_state',
    "[I, {saw, watched} $movie=#MOVIELOOKUP()]")
df.add_system_transition('initiation_state', 'response_state',
    "I've seen $movie too. {Did you like it?, You liked it, right?}")
df.add_user_transition('initiation_state', 'like_state',
    "{#SENT(positive), [yes]}")
df.add_user_transition('initiation_state', 'dislike_state',
    "{#SENT(negative), [no]}")
df.set_error_successor('initiation_state', 'error_state')
df.add_system_transition('error_state', 'response_state',
    "Sorry, I didn't catch that. Did you like $movie?")

df.run()