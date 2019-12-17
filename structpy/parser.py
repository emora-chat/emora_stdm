from collections import defaultdict
from lark import Lark


_symbol_string = r"""SYMBOL_STRING: /[a-z][a-z0-9_\s]*[a-z0-9_]|[a-z]/"""

_graph_grammar = r"""
    graph: statement (_CONJUNCTION_SEPARATOR statement)*
    statement: assertion | predicate
    predicate: relation _OPEN_PARENTHESIS (variable | symbol) _ARG_SEPARATOR (variable | symbol) _CLOSE_PARENTHESIS  [":" relation_name]
    assertion: symbol
    relation: (symbol | variable)
    SPECIAL_MARKER: "*"
    relation_variable: VAR_STRING [SPECIAL_MARKER] [scores]
    relation_symbol: SYMBOL_STRING [SPECIAL_MARKER] [scores]
    relation_name: relation_variable | relation_symbol
    variable: VAR_STRING [SPECIAL_MARKER] [scores]
    VAR_STRING: /[A-Z][A-Za-z0-9_\s]*[A-Za-z0-9_]|[A-Z]/
    symbol: SYMBOL_STRING [SPECIAL_MARKER] [scores]
    scores: "[" (score ",")* score "]"
    score: SCORE_TYPE ":" FLOAT
""" + _symbol_string + r"""
    COMMENT: /\/\/[^\n]*/
    _CONJUNCTION_SEPARATOR: ","
    _ARG_SEPARATOR: ","
    _OPEN_PARENTHESIS: "("
    _CLOSE_PARENTHESIS: ")"
    SCORE_TYPE: /[A-Za-z0-9_\s]*[A-Za-z0-9_]|[A-Z]/
    FLOAT: /[0-9.]+/

    %import common.WS
    %ignore WS
"""

_knowledge_parser = Lark(_graph_grammar, start='graph')

def _tree_to_kg(tree):
    """
    convert an abstract syntax tree into a KnowledgeGraph
    :param tree: lark tree structure defining a KnowledgeGraph
    """

    kg = KnowledgeGraph()

    if symbol_dict is None:
        symbol_dict = {}

    if node_dict is None:
        node_dict = {}

    # first pass to gather all unique strings as ids for variable or concept nodes
    for symbol in tree.find_data('symbol'):
        scores = {}
        expression = symbol.children[0].value
        if len(symbol.children) > 1 and hasattr(symbol.children[-1], 'data') and symbol.children[-1].data == 'scores':
            for score in symbol.children[-1].children:
                scores[score.children[0].value] = float(score.children[1].value)
        if expression not in node_dict:
            if expression in symbol_dict:
                symbol = symbol_dict[expression]
            else:
                symbol = None
            new_concept = Entity(expression, expression, scores)
            node_dict[expression] = new_concept
    for variable in tree.find_data('variable'):
        scores = {}
        identifier = variable.children[0].value
        if len(variable.children) > 1 and hasattr(variable.children[-1], 'data') and variable.children[-1].data == 'scores':
            for score in variable.children[-1].children:
                scores[score.children[0].value] = float(score.children[1].value)
        if identifier not in node_dict:
            new_variable = Variable(None, identifier, scores)
            node_dict[identifier] = new_variable

    #first-and-a-half pass to remove relation names from subject/object list
    # (so an error is thrown instead of generating multiple copies of one named relation)
    for rel_name in tree.find_data('relation_name'):
        try:
            del node_dict[rel_name.children[0].children[0].value]
        except KeyError:
            pass

    # todo: cannot currently add scores to relations
    #second pass to add all predicate triples to the kg
    for statement in tree.find_data('statement'):
        statement = statement.children[0]
        if statement.data == 'assertion':
            assert_id = statement.children[0].children[0].value
            kg.add_entity(node_dict[assert_id])
        elif statement.data == 'predicate':
            subject_name = statement.children[1].children[0].value
            relation_type_name = statement.children[0].children[0].children[0].value
            object_name = statement.children[2].children[0].value
            subject = node_dict[subject_name]
            relation_type = node_dict[relation_type_name]
            object = node_dict[object_name]
            relation_is_var = relation_var_default
            relation_name = None
            relation_branch = list(statement.find_data('relation_name'))
            if len(relation_branch) > 0:
                relation = relation_branch[0].children[0]
                relation_name = relation.children[0].value
                if relation.data == 'relation_variable':
                    relation_is_var = True
            if relation_is_var:
                new_relation = VariableRelation(subject, relation_type, object, None, relation_name)
            else:
                new_relation = Relation(subject, relation_type, object, representation=relation_name)
            if relation_name is not None:
                node_dict[relation_name] = new_relation
            else:
                node_dict[new_relation.representation()] = new_relation
            kg.add_relation(new_relation)

    special_nodes = set()
    for kind in ['symbol', 'variable', 'relation_symbol', 'relation_variable']:
        for sym in tree.find_data(kind):
            if len(sym.children) > 1:
                special_nodes.add(node_dict[sym.children[0]])

    return kg, special_nodes
