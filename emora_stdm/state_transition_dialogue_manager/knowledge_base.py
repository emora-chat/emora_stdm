
from structpy.graph.labeled_digraph import MapMultidigraph
from structpy.graph import Database
from structpy.graph.traversal import preset as traversal
import json
from collections import defaultdict

Graph = Database(MapMultidigraph)

_type = 'type'
_attr = 'attr'

_query_grammar = r"""
start: lemmatized_query | normal_query
lemmatized_query: "~" "#" start_node (":" (reversed_relation_type | normal_relation_type))+ "#"
normal_query: "#" start_node (":" (reversed_relation_type | normal_relation_type))+ "#"
start_node: ontology_reference | variable_reference | node_reference
normal_relation_type: relation_type
reversed_relation_type: "/" relation_type
relation_type: ontology_reference | variable_reference | node_reference
ontology_reference: "&" (variable_reference | node_reference | lemma_reference) 
variable_reference: "$" /[a-z_A-Z0-9.]+/
node_reference: /[a-z_A-Z 0-9.]+/
lemma_reference: "~" variable_reference
"""

class KnowledgeBase(Graph):

    def __init__(self, arcs=None):
        Graph.__init__(self, arcs)

    def query(self, query_string):
       pass

    def add_type(self, subtype, type):
        self.add(subtype, type, _type)

    def add_attr(self, type, attribute):
        if _attr not in self.data(type):
            self.data(type)[_attr] = set()
        self.data(type)[_attr].add(attribute)

    def types(self, node):
        if self.has_node(node):
            s = set(traversal.BreadthFirstOnArcs(self, node, _type)) - {node}
            return s
        else:
            return set()

    def subtypes(self, node):
        if self.has_node(node):
            return set(traversal.BreadthFirstOnArcsReverse(self, node, _type)) - {node}
        else:
            return set()

    def to_json(self):
        ontology_arcs = defaultdict(list)
        relation_arcs = list()
        for s, o, r in self.arcs():
            if r == _type:
                ontology_arcs[o].append(s)
            else:
                relation_arcs.append([s, r, o])
        return json.dumps({'ontology': ontology_arcs, 'predicates': relation_arcs},
                          indent=4, sort_keys=True)

    def load_json(self, json_string):
        d = json.loads(json_string)
        ontology = d['ontology']
        relations = d['predicates']
        for k, l in ontology.items():
            for e in l:
                self.add(e, k, _type)
        for relation in relations:
            s, r, o = tuple(relation)
            self.add(s, o, r)
