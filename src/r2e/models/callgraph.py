import json
from typing import Optional
from pydantic import BaseModel
from enum import Enum, auto

from r2e.models.identifier import Identifier


class CodeElemType(Enum):
    """Enum for code elements."""

    BUILTIN = auto()
    API = auto()
    FUNCTION = auto()
    METHOD = auto()
    CLASS = auto()
    OTHER = auto()


class CallGraph(BaseModel):
    graph: dict[Identifier, list[Identifier]]
    id2type: Optional[dict[Identifier, CodeElemType]] = None

    def get(self, key, default=None):
        if default is None:
            default = []
        return self.graph.get(key, default)

    def get_type(self, key):
        if self.id2type is None:
            return CodeElemType.OTHER
        return self.id2type.get(key, CodeElemType.OTHER)

    def keys(self):
        return self.graph.keys()

    def values(self):
        return self.graph.values()

    def items(self):
        return self.graph.items()

    def __contains__(self, key):
        return key in self.graph

    def __getitem__(self, key):
        return self.graph[key]

    def __len__(self):
        return len(self.graph)

    def __delitem__(self, key):
        del self.graph[key]

    def __setitem__(self, key, value):
        self.graph[key] = value

    # helpers

    @classmethod
    def from_dict(
        cls, graph: dict[str, list[str]], types: dict[str, str]
    ) -> "CallGraph":

        cgraph = {
            Identifier(identifier=k): [Identifier(identifier=v) for v in vs]
            for k, vs in graph.items()
        }

        id2type = {Identifier(identifier=k): CodeElemType[v] for k, v in types.items()}

        return cls(graph=cgraph, id2type=id2type)

    @classmethod
    def from_json(cls, file_path: str) -> "CallGraph":
        with open(file_path, "r") as f:
            data = json.load(f)

            if "graph" not in data:
                return cls.from_dict(graph=data, types={})

            graph = data.get("graph", {})
            id2type = data.get("id2type", {})
            return cls.from_dict(graph=graph, types=id2type)

    def to_dict(self) -> dict[str, list[str]]:
        return {
            k.identifier: [v.identifier for v in vs] for k, vs in self.graph.items()
        }
