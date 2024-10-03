import os
import ast

from r2e.generators.context.base import ContextCreator
from r2e.generators.context.format import ContextFormatter, ContextFormat
from r2e.pat.callgraph.explorer import CallGraphExplorer
from r2e.pat.imports.resolver import ImportResolver
from r2e.models import Function, Method


class FullContextCreator(ContextCreator):
    """Class for creating full context for a function or method

    Args:
        func_meth (Function | Method): Function or Method object
        max_context_size (int): Maximum context size in # of tokens
    """

    def __init__(
        self,
        func_meth: Function | Method,
        max_context_size: int | None = None,
        format: ContextFormat = ContextFormat.MARKDOWN_FILES,
        filter_calls: bool = True,
    ):
        super().__init__(func_meth, max_context_size, format)
        self.context_type = "full"
        self.filter_calls = filter_calls
        self.cg_explorer = CallGraphExplorer(self.func_meth.repo)
        self.construct_context()

    def construct_context(self):
        """constructor for the context (type: full)"""

        if self.filter_calls:
            context_files = self.callee_files()
        else:
            context_files = self.imported_files()

        for file_path in context_files:
            if file_path == self.func_meth.file_path:
                continue

            # add each "called" file to the context
            with open(file_path, "r") as f:
                rel_path = self.full_to_rel_path(file_path)
                code = f.read()
                self.context += ContextFormatter.format(code, rel_path, self.format)
                self.file2code[rel_path] = code

        self.context += self.processed_fut_file()

        # trigger truncation if necessary
        if self.max_context_size and self.context_size > self.max_context_size:
            self.truncate_context()

    # helpers

    def callee_files(self) -> set[str]:
        """Get the set of files that the func_meth calls"""
        caller_id = self.func_meth.id
        callees: list = self.cg_explorer.get_callees_from_identifier(
            caller_id=caller_id
        )
        return {callee.file_path for callee in callees}

    def imported_files(self) -> set[str]:
        """Get the set of files that the func_meth's file imports"""
        with open(self.func_meth.file_path, "r") as f:
            tree = ast.parse(f.read())

        imported_files = set()
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                file_path = ImportResolver.resolve_import_path(
                    self.func_meth.file_path, node
                )

                if os.path.exists(file_path):
                    imported_files.add(file_path)

        return imported_files

    def processed_fut_file(self) -> str:
        """Get the file containing the func_meth and returns in-file context"""
        with open(self.func_meth.file_path, "r") as f:
            code = f.read()

        assert self.func_meth.name is not None, "Function name not available"

        code, func_code = self._remove_func_class_from_file(code, self.func_meth)
        code = code + "\n\n" + func_code
        rel_path = self.full_to_rel_path(self.func_meth.file_path)
        fut_file_context = ContextFormatter.format(code.strip(), rel_path, self.format)
        self.file2code[rel_path] = code

        return fut_file_context
