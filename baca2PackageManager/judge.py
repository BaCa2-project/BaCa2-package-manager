from __future__ import annotations
from typing import Self, Any, Optional

from enum import Enum
from abc import ABC, abstractmethod


class JudgeVerdict(Enum):
    OK = 0
    FAIL = 1
    INCONCLUSIVE = 2


class JudgeNodeBase(ABC):

    def __init__(self, name: str):
        self._id = name

    def __hash__(self):
        return hash(self.name)

    @property
    def name(self) -> str:
        """:returns: a string value used for hashing an instance"""
        return self._id

    @abstractmethod
    def start(self, *args, **kwargs) -> Any:
        ...

    @abstractmethod
    def receive(self, *args, **kwargs) -> JudgeVerdict:
        ...


class EndNode(JudgeNodeBase):

    def __init__(self, name: str, end_node_meaning: JudgeVerdict):
        super().__init__(name)
        self.meaning = end_node_meaning

    def start(self, *args, **kwargs) -> Any:
        pass

    def receive(self, *args, **kwargs) -> JudgeVerdict:
        return self.meaning


class JudgeNodeError(ValueError):
    pass


class JudgeGraphIntegrityReport:
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
    def no_errors(self):
        return not (
                self.unreachable_nodes or
                self.cannot_reach_end or
                self.wrong_connections or
                not self.has_end_nodes)


class JudgeManager:

    def __init__(self):
        self.graph: dict[JudgeNodeBase, dict[JudgeVerdict, JudgeNodeBase]] = {}
        self._start_node: JudgeNodeBase = None

    @property
    def nodes(self) -> list[JudgeNodeBase]:
        return list(self.graph.keys())

    def get_node_by_name(self, name: str) -> JudgeNodeBase:
        for node in self.nodes:
            if node.name == name:
                return node
        else:
            raise JudgeNodeError(f"No node with name {name}.")

    def set_start_node(self, node: JudgeNodeBase):
        if node not in self.graph:
            raise KeyError(repr(node))
        self._start_node = node

    def get_start_node(self) -> JudgeNodeBase:
        if self._start_node is None:
            raise JudgeNodeError("Start_node is not set.")
        return self._start_node

    @classmethod
    def from_dict(cls,
                  dct: dict[JudgeNodeBase, dict[JudgeVerdict, JudgeNodeBase]],
                  start_node: JudgeNodeBase) -> Self:
        out = cls()
        for node in dct:
            out.add_node(node)
        for from_node, adj_list in dct.items():
            for verdict, to_node in adj_list.items():
                out.add_connection(from_node, to_node, verdict)
        out.set_start_node(start_node)
        return out

    def add_node(self, node: JudgeNodeBase):
        if node in self.graph:
            raise JudgeNodeError(f"Node with name '{node.name}' has already been added.")
        self.graph[node] = {}

    def add_connection(self, from_node: JudgeNodeBase, to_node: JudgeNodeBase, with_verdict: JudgeVerdict):
        if isinstance(from_node, EndNode):
            raise ResourceWarning(f"Connections from EndNodes will never be used.")
        adj_list = self.graph[from_node]
        if to_node not in self.graph:
            raise KeyError(repr(to_node))
        adj_list[with_verdict] = to_node

    def remove_node(self, node: JudgeNodeBase):
        del self.graph[node]
        for key in self.graph:
            adj_list = self.graph[key]
            new_adj_list = {a: b for a, b in adj_list.items() if b is not node}
            self.graph[key] = new_adj_list

    def remove_connection_by_node(self, from_node: JudgeNodeBase, to_node: JudgeNodeBase):
        adj_list = self.graph[from_node]
        tmp: JudgeNodeBase | None = None
        for key in adj_list:
            if adj_list[key] is to_node:
                tmp = key
                break
        if tmp is not None:
            del adj_list[tmp]
        else:
            raise KeyError("No connection")

    def remove_connection_by_verdict(self, from_node: JudgeNodeBase, verdict: JudgeVerdict):
        adj_list = self.graph[from_node]
        del adj_list[verdict]

    def send(self, node: JudgeNodeBase, *args, **kwargs) -> Any:
        if node not in self.graph:
            raise KeyError(repr(node))
        return node.start(*args, **kwargs)

    def receive(self, node: JudgeNodeBase | str | None = None, *args, **kwargs) -> JudgeNodeBase | None:
        """
        :returns: if node is not None: next node according to the graph, else: start_node
        """
        if node is None:
            return self.get_start_node()
        if isinstance(node, str):
            node = self.get_node_by_name(node)

        if isinstance(node, EndNode):
            raise TypeError("'node' cannot be an EndNode")
        adj_list = self.graph[node]
        verdict = node.receive(*args, **kwargs)
        return adj_list.get(verdict)

    def check_graph_integrity(self) -> JudgeGraphIntegrityReport:
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
