
from abc import ABC, abstractmethod

class Tree(ABC):
    """
    A tree with unordered children and a fixed root
    """

    @abstractmethod
    def root(self):
        """
        the root of the tree
        """
        pass

    @abstractmethod
    def children(self, node):
        """
        Get the children

        **node**: focal node

        **return**: iterable<node>
        """
        pass

    @abstractmethod
    def parent(self, node):
        pass

    @abstractmethod
    def add_child(self, node, child):
        pass

    @abstractmethod
    def remove_child(self, node, child):
        pass
