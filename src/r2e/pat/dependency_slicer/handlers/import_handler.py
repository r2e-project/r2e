import os
import ast
from typing import TYPE_CHECKING

from r2e.pat.imports import ImportResolver
from r2e.pat.dependency_slicer.ast_statements import AstStatements
from r2e.pat.dependency_slicer.handlers.base_handler import BaseHandler

if TYPE_CHECKING:
    from r2e.pat.dependency_slicer.slicer_main import DependencySlicer


class ImportHandler(BaseHandler):
    def _handle(self):
        import_file = ImportResolver.resolve_import_path(
            self.ast_statements.file_path, self.ast_statement.stmt  # type: ignore
        )
        if not os.path.exists(import_file):
            # print(import_file, "does not exist")
            return
        if import_file == self.ast_statement.file_path:
            return
        ast_stmts = self.slicer.get_file_ast_stmts(import_file)

        past_statement = ast_stmts.resolve_last_stmt(self.search_key)

        if past_statement is None:
            return

        self._add_past_statement(past_statement, self.search_key, ast_stmts)
