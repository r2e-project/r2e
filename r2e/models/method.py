import ast
from typing import Optional

from pydantic import BaseModel, validator

from r2e.models.file import File
from r2e.models.repo import Repo
from r2e.models.classes import Class
from r2e.models.module import Module
from r2e.models.identifier import Identifier
from r2e.utils.models import get_module_from_identifier
from r2e.models.context import Context
from r2e.pat.callgraph.explorer import CallGraphExplorer


class Method(BaseModel):
    method_id: Identifier
    file: File
    method_code: str
    method_name: Optional[str] = None
    parent_class_id: Optional[Identifier] = None
    context: Optional[Context] = None

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
    def name(self) -> None | str:
        return self.method_name

    @property
    def id(self) -> str:
        return self.method_id.identifier

    @property
    def code(self) -> str:
        return self.method_code

    @property
    def code_ast(self) -> ast.FunctionDef:
        return ast.parse(self.code).body[0]  # type: ignore

    @property
    def callees(self) -> list:
        cg_explorer = CallGraphExplorer(self.repo)
        callees = cg_explorer.get_callees_from_identifier(self.id)
        return callees

    @property
    def callee_count(self) -> int:
        cg_explorer = CallGraphExplorer(self.repo)
        callee_count = cg_explorer.get_callee_count(self.id)
        return callee_count

    @property
    def num_code_lines(self) -> int:
        num_lines = 0
        for idx, body_stmt in enumerate(self.code_ast.body):
            if (
                idx == 0
                and isinstance(body_stmt, ast.Expr)
                and isinstance(body_stmt.value, ast.Constant)
                and isinstance(body_stmt.value.value, str)
            ):
                continue
            num_lines += ast.unparse(body_stmt).count("\n") + 1
        return num_lines

    # helpers

    @validator("method_name", pre=True, always=True)
    def set_method_name(cls, v, values):
        if v is not None:
            return v

        method_id = values.get("method_id")
        method_name = method_id.identifier.split(".")[-1]
        return method_name

    @validator("parent_class_id", pre=True, always=True)
    def set_parent_class_id(cls, v, values):
        if v is not None:
            return v

        method_id = values.get("method_id")
        parent_class_id = Identifier(
            identifier=".".join(method_id.identifier.split(".")[:-1])
        )
        return parent_class_id

    def add_context(self, context: Context):
        self.context = context

    @classmethod
    def from_id_and_repo(cls, method_id: Identifier, repo: Repo) -> "Method":
        module: Module = get_module_from_identifier(method_id, repo)

        return cls(
            method_id=method_id,
            file=File(file_module=module),
            method_code="",
        )

    @property
    def parent_class(self) -> Class:
        assert self.parent_class_id is not None
        return Class.from_id_and_repo(
            class_id=self.parent_class_id,
            repo=self.repo,
        )

    @property
    def class_name(self) -> str | None:
        return self.parent_class.class_name
