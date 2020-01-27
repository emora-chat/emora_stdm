
from structpy.graph.labeled_digraph import MapMultidigraph
from structpy.graph import Database
from structpy.graph.traversal import preset as traversal
import json
from collections import defaultdict

Graph = Database(MapMultidigraph)

_type = 'type'
_attr = 'attr'


class KnowledgeBase(Graph):

    def __init__(self, arcs=None):
        Graph.__init__(self, arcs)

    def add_type(self, subtype, type):
        self.add(subtype, type, _type)

    def add_attr(self, type, attribute):
        if _attr not in self.data(type):
            self.data(type)[_attr] = set()
        self.data(type)[_attr].add(attribute)

    def type_check(self, value, type):
        words = value.split()
        for i in range(len(words)):
            for j in range(len(words), i, -1):
                partial = ' '.join(words[i:j])
                s = self.types(partial)
                if type in s:
                    return partial
        return False

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

    def attribute(self, rings):
        """
        :param rings: dict<str: node,
                           tuple<
                                 bool: negated,
                                 list<tuple<bool: reversed, str: relation>>>>
        :return: set<str: node>
        """
        result = None
        negs = set()
        for node, ring in rings.items():
            node = node.strip()
            negated, attr_chain = ring
            link = {node}
            for reverse, attr in attr_chain:
                attr = attr.strip()
                if attr == '*':
                    attr = None
                if not reverse:
                    link = set().union(*[self.targets(n, attr)
                                       for n in link if attr is None or self.has_arc_label(n, attr)])
                else:
                    link = set().union(*[self.sources(n, attr)
                                       for n in link if attr is None or self.has_in_arc_label(n, attr)])
            if negated:
                negs.update(link)
            else:
                if result is None:
                    result = link
                else:
                    result.intersection_update(link)
        return result - negs

    def valid_attribute(self, value, rings):
        s = self.attribute(rings)
        words = value.split()
        for i in range(len(words)):
            for j in range(len(words), i, -1):
                partial = ' '.join(words[i:j])
                if partial in s:
                    return partial
        return False

    def to_json(self):
        ontology_arcs = defaultdict(list)
        relation_arcs = list()
        for s, o, r in self.arcs():
            if r == _type:
                ontology_arcs[o].append(s)
            else:
                relation_arcs.append([s, r, o])
        return json.dumps({'ontology': ontology_arcs, 'predicates': relation_arcs}, indent=4, sort_keys=True)

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
