import ast
from typing import Optional, Any
import typing_extensions
from pydantic import BaseModel, BaseConfig, Field, validator

from r2e.models.repo import Repo
from r2e.models.file import File
from r2e.models.module import Module
from r2e.models.identifier import Identifier
from r2e.models.context import Context
from r2e.utils.models import get_module_from_identifier, get_module_from_path
from r2e.pat.callgraph.explorer import CallGraphExplorer


class Function(BaseModel):
    function_id: Identifier
    file: File
    function_code: str
    function_name: Optional[str] = None
    function_complexity: Optional[str] = None
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
        return self.function_name

    @property
    def id(self) -> str:
        return self.function_id.identifier

    @property
    def code(self) -> str:
        return self.function_code

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
        return cg_explorer.get_callee_count(self.id)

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

    @validator("function_name", pre=True, always=True)
    def populate_function_name(cls, v, values):
        function_id: Identifier = values.get("function_id")
        if v is None:
            return function_id.identifier.split(".")[-1]
        return v

    def add_context(self, context: Context):
        self.context = context

    @classmethod
    def from_id_and_repo(cls, function_id: Identifier, repo: Repo) -> "Function":
        module: Module = get_module_from_identifier(function_id, repo)

        return cls(
            function_id=function_id,
            file=File(file_module=module),
            function_code="",
        )

    @classmethod
    def from_name_file_repo(
        cls, function_name: str, local_file_path: str, repo: Repo
    ) -> "Function":
        pass
        module: Module = get_module_from_path(local_file_path, repo)
        module_identifier = module.module_id.identifier
        function_id = Identifier(identifier=module_identifier + "." + function_name)
        return cls(
            function_id=function_id,
            file=File(file_module=module),
            function_code="",
        )
