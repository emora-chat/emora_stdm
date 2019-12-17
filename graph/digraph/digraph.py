
from abc import ABC, abstractmethod
from structpy.graph import Node

class Digraph(ABC):

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
    def add_arc(self, source, target):
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
    def targets(self, source):
        """

        """
        pass

    @abstractmethod
    def sources(self, target):
        """

        """
        pass

    def arcs(self, node=None):
        """

        """
        raise NotImplementedError('laziness')

    def arcs_out(self, node):
        raise NotImplementedError()

    def arcs_in(self, node):
        raise NotImplementedError()

    def len_nodes(self):
        """

        """
        return len(self.nodes())

    def len_arcs(self):
        """

        """
        return len(self.arcs())

    def node(self, node_value):
        """

        """
        return Node(node_value, self)

    def add(self, node, target=None):
        if not self.has_node(node):
            self.add_node(node)
        if target is not None:
            if not self.has_node(target):
                self.add_node(target)
            self.add_arc(node, target)

    def has_node(self, node):
        return node in self.nodes()

    def has_arc(self, source, target):
        return (source, target) in self.arcs()

    def copy(self, other):
        raise NotImplementedError()
