
from abc import ABC, abstractmethod
from structpy.graph.element import Node
from structpy.graph.labeled_graph.labeled_graph_base import LabeledGraphBase


class LabeledDigraph(LabeledGraphBase, ABC):

    @abstractmethod
    def nodes(self):
        """

        """
        pass

    @abstractmethod
    def add_node(self, node):
        """

        """
        pass

    @abstractmethod
    def add_arc(self, source, target, label):
        """

        """
        pass

    @abstractmethod
    def remove_node(self, node):
        """

        """
        pass

    @abstractmethod
    def remove_arc(self, source, target):
        """

        """
        pass

    @abstractmethod
    def targets(self, source, label=None):
        """

        """
        pass

    @abstractmethod
    def label(self, source, target):
        """

        """
        pass

    @abstractmethod
    def sources(self, target, label=None):
        """

        """
        pass

    def arcs(self, node=None):
        """

        """
        if node is None:
            arcs = set()
            for node in self.nodes():
                arcs.update(self.arcs_out(node))
            return arcs
        else:
            return self.arcs_out(node).update(self.arcs_in(node))

    def arcs_out(self, node, label=None):
        if label is None:
            arcs = set()
            for target in self.targets(node):
                label = self.label(node, target)
                arcs.add((node, target, label))
            return arcs
        else:
            arcs = set()
            for target in self.targets(node, label):
                arcs.add((node, target, label))
            return arcs

    def arcs_in(self, node, label=None):
        if label is None:
            arcs = set()
            for source in self.sources(node):
                label = self.label(source, node)
                arcs.add((source, node, label))
            return arcs
        else:
            arcs = set()
            for source in self.sources(node, label):
                arcs.add((source, node, label))
            return arcs

    def len_nodes(self):
        """

        """
        return len(self.nodes())

    def len_arcs(self):
        """

        """
        return len(self.arcs())

    def add(self, node, target=None, label=None):
        if not self.has_node(node):
            self.add_node(node)
        if target is not None:
            if not self.has_node(target):
                self.add_node(target)
            self.add_arc(node, target, label)

    def has_node(self, node):
        return node in self.nodes()

    def has_arc(self, source, target, label=None):
        if label is None:
            for s, t, l in self.arcs():
                if s == source and t == target:
                    return True
            return False
        else:
            return (source, target, label) in self.arcs()

    def copy(self):
        new = self.__class__()
        new.update(self)
        return new

    def update(self, other):
        for arc in other.arcs():
            self.add(*arc)
