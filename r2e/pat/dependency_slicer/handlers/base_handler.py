import logging
from typing import TYPE_CHECKING

from r2e.logger import slicer_logger
from r2e.pat.dependency_slicer.globals_finder import find_dependency_globals
from r2e.pat.dependency_slicer.ast_statements import AstStatement, AstStatements

if TYPE_CHECKING:
    from r2e.pat.dependency_slicer.slicer_main import DependencySlicer


class BaseHandler:
    def __init__(
        self,
        ast_statement: AstStatement,
        ast_statements: AstStatements,
        search_key: str,
        slicer: "DependencySlicer",
        depth: int = -1,
    ):
        self.ast_statement = ast_statement
        self.ast_statements = ast_statements
        self.index = self.ast_statement.idx
        self.search_key = search_key
        self.slicer = slicer
        self.depth = depth

    def add_self_to_recursion_stack(self):
        """Add the current function to the recursion stack"""
        self.slicer.recursion_stack.append(self.ast_statement)

    def pop_recursion_stack(self):
        """Remove the current function from the recursion stack"""
        self.slicer.recursion_stack.pop()

    def exists_in_recursion_stack(self):
        """Check if the node is already in the recursion stack"""
        return self.ast_statement in self.slicer.recursion_stack

    def add_to_visited(self):
        """Add the node to the visited set"""
        self.slicer.visited_set.add(self.ast_statement)

    def exists_in_visited(self):
        """Check if the node is already visited"""
        return self.ast_statement in self.slicer.visited_set

    def _preprocess(self):
        """Check if the node is already visited or in recursion stack and add it to the stack otherwise"""
        if self.exists_in_recursion_stack():
            return True

        if self.exists_in_visited():
            return True

        # add current function to the stack
        self.add_self_to_recursion_stack()

        return False

    def _postprocess(self):
        """Remove the node from the recursion stack and add it to the visited set"""
        self.pop_recursion_stack()
        self.add_to_visited()

    def _add_past_statement(
        self,
        past_statement: AstStatement,
        symbol: str,
        ast_statements: AstStatements | None = None,
    ):
        ## add to dependency
        self.slicer.dependency_graph.add_edge(
            self.ast_statement,
            past_statement,
            symbol,
        )

        ## visit the past statement
        if ast_statements is None:
            self.slicer.visit(
                past_statement, self.ast_statements, symbol, depth=self.depth - 1
            )
        else:
            self.slicer.visit(
                past_statement, ast_statements, symbol, depth=self.depth - 1
            )

    def _add_globals(self):
        # visit all the global accesses
        for symbol in self.global_access_symbols:
            # for every symbol
            # resolve past statement
            past_statement = self.ast_statements.resolve_last_stmt(symbol, self.index)
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
        return

    def _handle(self):
        """Type specific handling details empty by default.
        To be implemented by subclasses as needed."""
        return

    def handle(self):
        # check if already visited
        exit = self._preprocess()
        if exit:
            return

        # find all globals
        self.global_access_symbols = find_dependency_globals(
            self.ast_statement.stmt, unique=True
        )

        # recurse and add to dependency graph
        self._add_globals()

        # ast type specific handling details
        self._handle()

        # add to visited set
        self._postprocess()
