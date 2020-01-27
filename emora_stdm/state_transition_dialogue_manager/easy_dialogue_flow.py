

'''

class MyDialogueFlow(EasyDialogueFlow):

    class States(EasyDialogueStates):
        A = 0
        B = 1
        C = 2

    transitions = [
        UserTransition(States.A, States.B, 'i am $hobby=ONT(hobby) {now, today}'),
        SystemTransition(States.B, States.C, '$hobby is cool')
    ]


class StateEnum(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name

class DialogueHandler(DialogueFlow):
    def __init__(self):
        self.states = self.init_states()
        self.init_transition()


    @abs.method
    def init_states(self) -> StateEnum:
        pass

    def init_tran(self):
        self.add_transition(self.states.ABC)


 class MyDialogueHandler(DialogueHandler):



def main():
    handlers = [MyDialogueHandler(), SDFDS]
    for handler in handlers: handler.run()
    # my_hanlder = MyDialogueHandler()
    # my_handler.run()

'''