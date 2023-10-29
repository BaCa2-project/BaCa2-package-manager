
from typing import Any
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
        raise RuntimeError("EndNode.start should never be called")

    def receive(self, *args, **kwargs) -> JudgeVerdict:
        return self.meaning


class JudgeManager:

    def __init__(self):
        default_end_node = EndNode("!SUCCESS", JudgeVerdict.OK)
        self.graph: dict[JudgeNodeBase, dict[JudgeVerdict, JudgeNodeBase]] = {default_end_node: {}}
        self.start_node: JudgeNodeBase = None

    @property
    def nodes(self) -> list[JudgeNodeBase]:
        return [key for key in self.graph]

    @classmethod
    def from_dict(cls, dct: dict[JudgeNodeBase, dict[JudgeVerdict, JudgeNodeBase]]) -> 'JudgeManager':
        out = cls()
        for node in dct:
            out.add_node(node)
        for from_node, adj_list in dct.items():
            for verdict, to_node in adj_list.items():
                out.add_connection(from_node, to_node, verdict)
        return out

    def set_start_node(self, node: JudgeNodeBase):
        if node not in self.graph:
            raise KeyError(repr(node))
        self.start_node = node

    def add_node(self, node: JudgeNodeBase) -> None:
        if len(node.name) > 0 and node.name[0] == '!':
            raise EncodingWarning("'!' character at the beginning is reserved for special-purpose nodes.")
        if node in self.graph:
            raise ValueError(f"Node with name '{node.name}' has already been added.")
        self.graph[node] = {}

    def add_connection(self, from_node: JudgeNodeBase, to_node: JudgeNodeBase, with_verdict: JudgeVerdict):
        if isinstance(from_node, EndNode):
            raise ResourceWarning(f"Connections from EndNodes will never be used.")
        adj_list = self.graph[from_node]
        if to_node not in self.graph:
            raise KeyError(repr(to_node))
        adj_list[with_verdict] = to_node

    def remove_node(self, node: JudgeNodeBase):
        if len(node.name) > 0 and node.name[0] == '!':
            raise ValueError("Cannot delete special-purpose nodes.")
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

    def receive(self, node: JudgeNodeBase | None = None, *args, **kwargs) -> JudgeNodeBase | None:
        if isinstance(node, EndNode):
            raise TypeError("'node' cannot be an EndNode")
        if node is None:
            node = self.start_node
        adj_list = self.graph[node]
        verdict = node.receive(*args, **kwargs)
        return adj_list.get(verdict)
