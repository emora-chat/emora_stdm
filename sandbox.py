
from expression import Expression as E
from dialogue_flow import DialogueFlow, DialogueTransition
import expression


if __name__ == '__main__':


    i = 'this is (a, the) [test {some, something, for ya} ok] there'
    while True:
        tree = expression._expression_parser.parse(i)
        print(tree.pretty())
        print('-' * 79)
        exp = expression.init(i)
        print(exp)
        i = input('U: ')


