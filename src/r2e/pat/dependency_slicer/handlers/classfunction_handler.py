import ast
import logging
from typing import TYPE_CHECKING

from r2e.logger import slicer_logger
from r2e.models import Function, Class, Method
from r2e.pat.ast.explorer import body_import_finder
from r2e.pat.dependency_slicer.ast_statements import AstStatements
from r2e.pat.dependency_slicer.handlers.base_handler import BaseHandler


if TYPE_CHECKING:
    from r2e.pat.dependency_slicer.slicer_main import DependencySlicer


class ClassFunctionHandler(BaseHandler):

    def _add_globals(self):
        # visit all the global accesses
        for symbol in self.global_access_symbols:
            # for every symbol
            # resolve past statement
            past_statement = self.ast_statements.resolve_last_stmt(symbol)
            if past_statement is None:
                all_wildcard_imports = self.ast_statements.resolve_wildcard_imports()
                if len(all_wildcard_imports) == 0:
                    slicer_logger.log(
                        logging.INFO,
                        f"Cannot resolve symbol {symbol} @ {self.ast_statement}",
                    )
                    continue
                for wildcard_import in all_wildcard_imports:
                    self._add_past_statement(wildcard_import, symbol)
                continue

            ## add to dependency
            self._add_past_statement(past_statement, symbol)

    def _handle_callees(self):
        if self.slicer.callgraph_explorer is None:
            return
        callees = self.slicer.callgraph_explorer.get_callees(
            self.ast_statement.file, self.ast_statement.stmt.name  # type: ignore
        )

        for callee in callees:
            if isinstance(callee, Function):
                ast_stmts = self.slicer.get_file_ast_stmts(callee.file_path)
                assert callee.function_name is not None
                callee_aststmt = ast_stmts.find_function_stmt_with_name(
                    callee.function_name
                )

                if callee_aststmt is None:
                    # print(f"Cannot find {type(callee)=}|{callee} in {ast_stmts.file}")
                    continue

                self._add_past_statement(
                    callee_aststmt, callee.function_name, ast_stmts
                )
            elif isinstance(callee, Class):
                ast_stmts = self.slicer.get_file_ast_stmts(callee.file_path)
                assert callee.class_name is not None
                callee_aststmt = ast_stmts.find_class_stmt_with_name(callee.class_name)

                if callee_aststmt is None:
                    # print(f"Cannot find {type(callee)=}|{callee} in {ast_stmts.file}")
                    continue

                self._add_past_statement(callee_aststmt, callee.class_name, ast_stmts)
            elif isinstance(callee, Method):
                callee = callee.parent_class
                assert callee.class_name is not None
                ast_stmts = self.slicer.get_file_ast_stmts(callee.file_path)
                callee_aststmt = ast_stmts.find_class_stmt_with_name(callee.class_name)

                if callee_aststmt is None:
                    # print(f"Cannot find {type(callee)=}|{callee} in {ast_stmts.file}")
                    continue

                self._add_past_statement(callee_aststmt, callee.class_name, ast_stmts)
            else:
                raise ValueError(f"Unknown callee type {callee}")

    def _handle_internal_imports(self):
        internal_imports = body_import_finder(self.ast_statement.stmt)  # type: ignore
        new_imports: list[ast.Import | ast.ImportFrom] = []
        for internal_import in internal_imports:
            new_imports.extend(
                AstStatements.transform_imports(
                    self.ast_statement.file_path, internal_import
                )
            )

        for new_import in new_imports:
            fake_ast_stmt = self.ast_statements.create_fake_import_aststmt(new_import)
            self.slicer.visit(fake_ast_stmt, self.ast_statements, "-1")

    def _handle(self):
        """
        Uses the call graph to find the dependencies of the function.
        The dependencies are going to be functions or classes only.
        """
        stmt = self.ast_statement.stmt
        assert isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))

        self._handle_callees()
        self._handle_internal_imports()

        return
