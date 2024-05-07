import ast
from pydantic import BaseModel, validator
from typing import Optional

from r2e.models.file import File
from r2e.models.identifier import Identifier
from r2e.models.repo import Repo
from r2e.models.module import Module
from r2e.utils.models import get_module_from_identifier
from r2e.pat.callgraph.explorer import CallGraphExplorer


class Class(BaseModel):
    class_id: Identifier
    file: File
    class_name: Optional[str] = None

    _method_ids: Optional[list[Identifier]] = None

    @property
    def file_path(self) -> str:
        return self.file.file_path

    @property
    def repo(self) -> Repo:
        return self.file.repo

    @property
    def _repo_name(self) -> str:
        return self.file._repo_name

    @property
    def repo_id(self) -> str:
        return self.file.repo_id

    @property
    def module(self) -> Module:
        return self.file.file_module

    @property
    def id(self) -> str:
        return self.class_id.identifier

    @property
    def callees(self) -> list:
        cg_explorer = CallGraphExplorer(self.repo)
        callees = cg_explorer.get_callees_from_identifier(self.id)
        return callees

    @property
    def method_ids(self) -> list[Identifier]:
        # methods of class are the ids w/ the prefix `class_id.`
        # and same number of dots as the `class_id.`

        if self._method_ids is not None:
            return self._method_ids

        if self.repo.callgraph is None:
            raise ValueError("Callgraph not found in the repo")

        if self.repo.callgraph.id2type is None:
            raise ValueError("Callgraph id2type not found in the repo")

        cgraph_ids = [k.identifier for k in self.repo.callgraph.id2type.keys()]
        class_id_str = self.class_id.identifier
        prefix = class_id_str + "."

        method_ids = [
            Identifier(identifier=id_str)
            for id_str in cgraph_ids
            if id_str.startswith(prefix) and id_str.count(".") == prefix.count(".")
        ]

        self._method_ids = method_ids

        return self._method_ids

    # helpers

    @validator("class_name", pre=True, always=True)
    def set_class_name(cls, v, values):
        if v is not None:
            return v

        class_id = values.get("class_id")
        class_name = class_id.identifier.split(".")[-1]
        return class_name

    @classmethod
    def from_id_and_repo(cls, class_id: Identifier, repo: Repo) -> "Class":
        module: Module = get_module_from_identifier(class_id, repo)

        return cls(
            class_id=class_id,
            file=File(file_module=module),
        )
