from __future__ import annotations
from typing import Self, Any

from enum import Enum
from abc import ABC, abstractmethod

import pickle


class JudgeVerdict(Enum):
    """Judge Verdict"""
    OK = 0
    FAIL = 1
    INCONCLUSIVE = 2


class JudgeNodeBase(ABC):
    """
    Abstract base for 'Judge Nodes' of decision graphs in 'JudgeMaster' class.

    A 'JudgeNode' is supposed to represent a single step in a process of submit checking.
    It should implement a specific test for submits and return a verdict in form of the
    'JudgeVerdict' class instance.
    """

    def __init__(self, name: str):
        """
        Initiate JudgeNodeBase.

        :param name: a unique identifier
        :type name: str
        """
        self._id = name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        if not isinstance(other, JudgeNodeBase):
            return False
        return self.name == other.name

    @property
    def name(self) -> str:
        """
        Returns a string used for identification purposes

        :return: a string used for identification purposes
        """
        return self._id

    @abstractmethod
    def start(self, *args, **kwargs) -> Any:
        """
        Starts judging process.
        This method should initiate checking process for a submit which in the end
        should call the 'receive' method of the same instance.
        """
        ...

    @abstractmethod
    def receive(self, *args, **kwargs) -> JudgeVerdict:
        """
        Receives judging results and returns a verdict.
        This method should be called after the 'start' method and the process it
        had initiated.

        :return: a verdict used for traversing the decision graph in JudgeMaster
        """
        ...

    def serialise(self) -> bytes:
        return pickle.dumps(self)

    @classmethod
    def unpack(cls, binary_data: bytes) -> Self:
        tmp = pickle.loads(binary_data)
        if not isinstance(tmp, cls):
            raise TypeError(f"Unpacked object is not of type {cls.__name__}")
        return tmp


class EndNode(JudgeNodeBase):
    """
    Special type of the 'JudgeNodeBase' class. Represents the final stage of submit checking
    process and yields the final verdict of all tests.
    """

    def __init__(self, name: str, end_node_meaning: JudgeVerdict):
        """
        Initiate an instance

        :param name: unique identifier
        :type name: str
        :param end_node_meaning: the final verdict of all tests
        :type end_node_meaning: JudgeVerdict
        """
        super().__init__(name)
        self.meaning = end_node_meaning

    def start(self, *args, **kwargs) -> Any:
        pass

    def receive(self, *args, **kwargs) -> JudgeVerdict:
        """
        Returns the final verdict. Ignores all arguments.

        :return: the final verdict
        """
        return self.meaning


class JudgeNodeError(ValueError):
    """Exception class used by JudgeMaster"""
    pass


class EndNodeError(JudgeNodeError):
    """Exception class used by JudgeMaster"""
    pass


class JudgeGraphIntegrityReport:
    """
    Data class used to hold information about errors in the decision graph in
    'JudgeMaster' class.

    attr unreachable_nodes: stores nodes to which no path from the start_node exists
    attr cannot_reach_end: stores nodes from which no path leads to any EndNode
    attr wrong connections: stores nodes for which edges are defined in a wrong way
    attr has_end_nodes: True if the decision graph has any end nodes, False otherwise
    """
    def __init__(self,
                 unreachable_nodes: list[JudgeNodeBase],
                 cannot_reach_end: list[JudgeNodeBase],
                 wrong_connections: list[JudgeNodeBase],
                 has_end_nodes: bool):
        self.unreachable_nodes = unreachable_nodes
        self.cannot_reach_end = cannot_reach_end
        self.wrong_connections = wrong_connections
        self.has_end_nodes = has_end_nodes

    @property
    def no_errors(self) -> bool:
        """Returns True if the decision graph is completely error free"""
        return not (
                self.unreachable_nodes or
                self.cannot_reach_end or
                self.wrong_connections or
                not self.has_end_nodes)


class JudgeManager:
    """Manages the decision graph of submit checking"""

    def __init__(self):
        self.graph: dict[JudgeNodeBase, dict[JudgeVerdict, JudgeNodeBase]] = {}
        self._start_node: JudgeNodeBase = None

    def __eq__(self, other):
        if not isinstance(other, JudgeManager):
            return False
        return self.graph == other.graph and self._start_node == other._start_node

    @property
    def nodes(self) -> list[JudgeNodeBase]:
        """:return: a list of all nodes in the graph"""
        return list(self.graph.keys())

    def get_node_by_name(self, name: str) -> JudgeNodeBase:
        """
        Looks for a node with name 'name'.

        :param name: name of the wanted node
        :return: the node with name 'name'
        :raise JudgeNodeError: if there is no node with name 'name'
        """
        for node in self.nodes:
            if node.name == name:
                return node
        else:
            raise JudgeNodeError(f"No node with name {name}.")

    def set_start_node(self, node: JudgeNodeBase):
        """Set start node. It is None by default"""
        if node not in self.graph:
            raise KeyError(repr(node))
        self._start_node = node

    def get_start_node(self) -> JudgeNodeBase:
        """
        Get start node.

        :return: the start node
        :raise JudgeNodeError: if start node is not set
        """
        if self._start_node is None:
            raise JudgeNodeError("Start_node is not set.")
        return self._start_node

    @classmethod
    def from_dict(cls,
                  dct: dict[JudgeNodeBase, dict[JudgeVerdict, JudgeNodeBase]],
                  start_node: JudgeNodeBase) -> Self:
        """
        Create a JudgeManager class instance using a dictionary.

        :param dct: a graph in form of an adjacency list
        :param start_node: the start node
        :return: a JudgeMaster class instance with the provided graph
        """
        out = cls()
        for node in dct:
            out.add_node(node)
        for from_node, adj_list in dct.items():
            for verdict, to_node in adj_list.items():
                out.add_connection(from_node, to_node, verdict)
        out.set_start_node(start_node)
        return out

    def add_node(self, node: JudgeNodeBase):
        """
        Add node to the graph. node.name has to be unique.

        :param node: the node to be added.
        :raise JudgeNodeError: if the node already belongs to the graph
        """
        if node in self.graph:
            raise JudgeNodeError(f"Node with name '{node.name}' has already been added.")
        self.graph[node] = {}

    def add_connection(self, from_node: JudgeNodeBase, to_node: JudgeNodeBase, with_verdict: JudgeVerdict):
        """
        Create a (directed) edge between to nodes and label it with verdict. If an edge with the
        provided verdict already exists it will be overwritten.

        :param from_node: the edge will begin at this node
        :param to_node: the edge will end at this node
        :param with_verdict: the edge will be labeled wit this verdict

        :raise KeyError: if from_node or to_node do not belong to the graph
        :raise ResourceWarning: if trying to add edges from EndNodes
        """
        if isinstance(from_node, EndNode):
            raise ResourceWarning(f"Connections from EndNodes will never be used.")
        adj_list = self.graph[from_node]
        if to_node not in self.graph:
            raise KeyError(repr(to_node))
        adj_list[with_verdict] = to_node

    def remove_node(self, node: JudgeNodeBase):
        """
        Remove the provided node and all edges leaving or entering this node from the graph.

        :param node: the node to be removed
        :raise KeyError: if the node does not belong to the graph
        """
        del self.graph[node]
        for key in self.graph:
            adj_list = self.graph[key]
            new_adj_list = {a: b for a, b in adj_list.items() if b is not node}
            self.graph[key] = new_adj_list

    def remove_connection_by_node(self, from_node: JudgeNodeBase, to_node: JudgeNodeBase):
        """
        Remove all edges between two specified nodes.

        :param from_node: the first node
        :param to_node: the last node
        :raise KeyError: if any of the nodes do not belong to the graph or there are no edges between them
        """
        adj_list = self.graph[from_node]
        tmp: list[JudgeNodeBase] = []
        for key in adj_list:
            if adj_list[key] is to_node:
                tmp.append(key)
        if tmp:
            for item in tmp:
                del adj_list[item]
        else:
            raise KeyError("No connections")

    def remove_connection_by_verdict(self, from_node: JudgeNodeBase, verdict: JudgeVerdict):
        """
        Remove an edge leaving from from_node labeled with the specified verdict

        :param from_node: the node for which an edge should be deleted
        :param verdict: label of the edge that should be deleted
        :raise KeyError: if the node or the edge do not exist
        """
        adj_list = self.graph[from_node]
        del adj_list[verdict]

    def send(self, node: JudgeNodeBase, *args, **kwargs) -> Any:
        """
        Invokes the 'send' method on the provided node with provided arguments.

        :param node: node to be used
        :raise KeyError: if the given node does not belong to the graph
        """
        if node not in self.graph:
            raise KeyError(repr(node))
        return node.start(*args, **kwargs)

    def advance(self, node: JudgeNodeBase | str, verdict: JudgeVerdict) -> JudgeNodeBase | None:
        """
        Advances the decision graph according to the provided verdict.

        :return: Next node according to the graph, if there is no edge for provided verdict: None
        :raise KeyError: if the given node does not belong to the graph
        :raise EndNodeError: if the given node is an EndNode
        """
        if isinstance(node, str):
            node = self.get_node_by_name(node)

        if isinstance(node, EndNode):
            raise EndNodeError("'node' cannot be an EndNode")
        return self.graph[node].get(verdict)

    def check_graph_integrity(self) -> JudgeGraphIntegrityReport:
        """
        Looks for errors in the decision graph and returns a report.

        :return: the report
        """
        reach_list = self._floyd_warshall()
        end_nodes = frozenset(node for node in self.nodes if isinstance(node, EndNode))

        # unreachable nodes searching
        unreachable: list[JudgeNodeBase] = list(frozenset(self.nodes).difference(reach_list[self._start_node]))

        # searching for nodes from which no EndNode is reachable
        cannot_reach_end: list[JudgeNodeBase] = []
        for node in self.nodes:
            if not end_nodes.intersection(reach_list[node]):
                cannot_reach_end.append(node)

        # checking for valid connections
        wrong_connections: list[JudgeNodeBase] = []
        for node in self.nodes:
            tmp = frozenset(self.graph[node].keys())
            if not (
                    {JudgeVerdict.OK, JudgeVerdict.FAIL}.issubset(tmp)
                    or {JudgeVerdict.OK, JudgeVerdict.INCONCLUSIVE}.issubset(tmp)
                    or isinstance(node, EndNode)
            ):
                wrong_connections.append(node)

        # check for end nodes
        has_end_nodes = len(end_nodes) != 0

        return JudgeGraphIntegrityReport(unreachable, cannot_reach_end, wrong_connections, has_end_nodes)

    def _floyd_warshall(self) -> dict[JudgeNodeBase, frozenset[JudgeNodeBase]]:
        node_list = self.nodes  # for performance
        nl_length = len(node_list)
        visit_matrix = [[j in self.graph[i].values() or i is j for j in node_list] for i in node_list]

        for k in range(nl_length):
            for i in range(nl_length):
                for j in range(nl_length):
                    visit_matrix[i][j] = visit_matrix[i][j] or (visit_matrix[i][k] and visit_matrix[k][j])

        out: dict[JudgeNodeBase, list[JudgeNodeBase]] = {}
        for index, node in enumerate(node_list):
            out[node] = frozenset(node_list[i] for i, b in enumerate(visit_matrix[index]) if b)

        return out

    def serialise(self) -> bytes:
        return pickle.dumps(self)

    @classmethod
    def unpack(cls, binary_data: str) -> Self:
        tmp = pickle.loads(binary_data)
        if not isinstance(tmp, cls):
            raise TypeError(f"Unpacked object is not of type {cls.__name__}")
        return tmp
