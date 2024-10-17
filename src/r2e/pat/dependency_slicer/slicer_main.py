import ast
from typing import Type

from r2e.models import Repo, File, Function, Class
from r2e.pat.callgraph import CallGraphExplorer
from r2e.pat.dependency_slicer.dependency_graph import DependencyGraph
from r2e.pat.dependency_slicer.ast_statements import AstStatement, AstStatements
from r2e.pat.dependency_slicer.handlers import (
    BaseHandler,
    ClassFunctionHandler,
    ImportHandler,
)


HandlersMapping: dict[Type[ast.AST], Type[BaseHandler]] = {
    ast.ClassDef: ClassFunctionHandler,
    ast.FunctionDef: ClassFunctionHandler,
    ast.AsyncFunctionDef: ClassFunctionHandler,
    ast.Import: ImportHandler,
    ast.ImportFrom: ImportHandler,
}


class DependencySlicer:
    """
    The slicing orchestrator class. It takes a function model and runs the slicing process.
    It keeps track of all the metadata required during the slicing process
        - initial function details for starting the slicing process
        - file_ast_cache to keep track of the AST of all the files visited
        - recursion stack to keep track of the current class/function being visited
        - visited set to keep track of all the classes/functions already visited
        - the two allow handing recursion and caching
        - dependency graph data structure
    All this information is filled in by the handlers during the slicing process.
    """

    def __init__(
        self,
        repo: Repo,
        ast_stmt_list: list[AstStatement],
        file_ast_cache: dict[str, AstStatements],
        depth: int = -1,
    ):
        self.repo = repo
        self.ast_stmt_list = ast_stmt_list
        self.file_ast_cache = file_ast_cache
        try:
            self.callgraph_explorer = CallGraphExplorer(self.repo)
        except Exception as e:
            print(repr(e))
            self.callgraph_explorer = None

        self.recursion_stack: list[AstStatement] = []
        self.visited_set: set[AstStatement] = set()

        self.dependency_graph = DependencyGraph(self.ast_stmt_list)

        self.depth = depth

    @classmethod
    def from_function_models(
        cls, function_models: Function | list[Function], depth: int = -1
    ):
        function_models = (
            function_models if isinstance(function_models, list) else [function_models]
        )
        assert (
            len(set([f.repo for f in function_models])) == 1
        ), f"{[f.repo for f in function_models]} are not the same repos"

        repo = function_models[0].repo

        file_ast_cache: dict[str, AstStatements] = {}

        ast_stmt_list: list[AstStatement] = []
        for function in function_models:
            assert function.function_name is not None
            if function.file_path in file_ast_cache:
                ast_stmts = file_ast_cache[function.file_path]
            else:
                ast_stmts = AstStatements(function.file)
                file_ast_cache[function.file_path] = ast_stmts

            resolved_function = ast_stmts.find_function_stmt_with_name(
                function.function_name
            )
            assert resolved_function is not None
            ast_stmt_list.append(resolved_function)

        return cls(repo, ast_stmt_list, file_ast_cache, depth)

    @classmethod
    def from_class_models(cls, class_models: Class | list[Class], depth: int = -1):
        class_models = (
            class_models if isinstance(class_models, list) else [class_models]
        )
        assert (
            len(set([c.repo for c in class_models])) == 1
        ), f"{[c.repo for c in class_models]} are not the same repos"

        repo = class_models[0].repo

        file_ast_cache: dict[str, AstStatements] = {}

        ast_stmt_list: list[AstStatement] = []
        for class_model in class_models:
            assert class_model.class_name is not None
            if class_model.file_path in file_ast_cache:
                ast_stmts = file_ast_cache[class_model.file_path]
            else:
                ast_stmts = AstStatements(class_model.file)
                file_ast_cache[class_model.file_path] = ast_stmts

            resolved_class = ast_stmts.find_class_stmt_with_name(class_model.class_name)
            assert resolved_class is not None
            ast_stmt_list.append(resolved_class)

        return cls(repo, ast_stmt_list, file_ast_cache, depth)

    def run(self):
        for ast_stmt in self.ast_stmt_list:
            self.visit(
                ast_stmt, self.file_ast_cache[ast_stmt.file_path], depth=self.depth
            )

    def visit(
        self,
        stmt: AstStatement,
        all_stmts: AstStatements,
        search_key: str = "",
        depth: int = -1,
    ):
        if depth == 0:
            return

        print(f"Visiting {stmt} with depth {depth}")
        if stmt in self.visited_set or stmt in self.recursion_stack:
            return
        for ast_type, handler in HandlersMapping.items():
            if isinstance(stmt.stmt, ast_type):
                handler_instance = handler(stmt, all_stmts, search_key, self, depth)
                handler_instance.handle()
                return
        BaseHandler(stmt, all_stmts, search_key, self, depth).handle()
        return

    def get_file_ast_stmts(self, file_path: str) -> AstStatements:
        if file_path in self.file_ast_cache:
            return self.file_ast_cache[file_path]

        file_obj = File.from_file_path(file_path, self.repo)
        ast_stmts = AstStatements(file_obj)
        self.file_ast_cache[file_path] = ast_stmts
        return ast_stmts
