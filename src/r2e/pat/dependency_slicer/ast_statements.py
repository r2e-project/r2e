import ast
import bisect
from copy import deepcopy
from collections import defaultdict

from r2e.models import File
from r2e.pat.imports import ImportTransformer
from r2e.pat.ast import build_ast, unparse_ast_stmt_with_comments


class AstStatement:
    def __init__(
        self,
        stmt: ast.stmt,
        idx: int,
        file: File,
        orig_stmt: ast.stmt,
        orig_stmt_idx: int,
    ) -> None:
        assert isinstance(stmt, ast.stmt)
        self.stmt = stmt
        self.idx = idx
        self.file = file
        self.orig_stmt = orig_stmt
        self.orig_stmt_idx = orig_stmt_idx

    @property
    def stmt_code(self) -> str:
        return ast.unparse(self.stmt)

    @property
    def file_path(self) -> str:
        return self.file.file_path

    def __str__(self) -> str:
        return f"{self.stmt} @ {self.file_path}"

    @property
    def unparse_stmt(self, with_comments=True) -> str:
        if with_comments:
            return unparse_ast_stmt_with_comments(self.file.file_content, self.stmt)
        return ast.unparse(self.orig_stmt)

    @property
    def unparse_idx(self) -> int:
        return self.orig_stmt_idx

    @property
    def unparse_tuple(self) -> tuple[int, str, str]:
        return (self.unparse_idx, self.unparse_stmt, self.file_path)


class AstStatements:
    def __init__(self, file: File) -> None:
        self.file = file
        self.statements_list = self.build_statements_list()
        self.var_to_stmt_idxs: dict[str, list[int]] = self.build_var_to_stmt_idxs()
        self.wildcard_idxs: list[int] = self.find_wildcard_imports()

    def create_fake_import_aststmt(
        self, import_stmt: ast.Import | ast.ImportFrom
    ) -> AstStatement:
        return AstStatement(import_stmt, -1, self.file, import_stmt, -1)

    @property
    def file_path(self) -> str:
        return self.file.file_path

    @staticmethod
    def transform_imports(
        file_path,
        stmt: ast.Import | ast.ImportFrom,
    ) -> list[ast.Import | ast.ImportFrom]:

        transformed_stmt = deepcopy(stmt)
        ImportTransformer.transform_import(file_path, transformed_stmt)  # type: ignore

        transformed_stmts: list[ast.Import | ast.ImportFrom] = []
        if isinstance(stmt, ast.Import):
            ## import a, b, c -> import a as a, b as b, c as c
            for alias in transformed_stmt.names:
                if alias.asname is None:
                    # import a.b.c adds a to the namespace
                    # import a.b.c as a
                    alias.asname = alias.name.split(".")[0]
                new_import = ast.Import(names=[alias])
                ast.copy_location(new_import, stmt)
                transformed_stmts.append(new_import)
        else:
            ## from x import y, z -> from x import y as y, from x import z as z
            for alias in transformed_stmt.names:
                if alias.asname is None:
                    # from x import y -> from x import y as y
                    if alias.name != "*":
                        alias.asname = alias.name

                new_import = ast.ImportFrom(
                    module=stmt.module, names=[alias], level=stmt.level
                )
                ast.copy_location(new_import, stmt)
                transformed_stmts.append(new_import)
        return transformed_stmts

    def transform_stmt(self, stmt: ast.stmt) -> list[ast.stmt]:
        if isinstance(stmt, (ast.Import, ast.ImportFrom)):
            transformed_imports = AstStatements.transform_imports(self.file_path, stmt)
            return transformed_imports  # type: ignore
        elif isinstance(stmt, ast.If):
            transformed_stmts = []
            for body_stmt in stmt.body:
                transformed_stmts.extend(self.transform_stmt(body_stmt))
            for orelse_stmt in stmt.orelse:
                transformed_stmts.extend(self.transform_stmt(orelse_stmt))
            return transformed_stmts
        elif isinstance(stmt, (ast.Try, ast.TryStar)):
            transformed_stmts = []
            for body_stmt in stmt.body:
                transformed_stmts.extend(self.transform_stmt(body_stmt))
            for handler in stmt.handlers:
                for handler_stmt in handler.body:
                    transformed_stmts.extend(self.transform_stmt(handler_stmt))
            for orelse_stmt in stmt.orelse:
                transformed_stmts.extend(self.transform_stmt(orelse_stmt))
            for final_stmt in stmt.finalbody:
                transformed_stmts.extend(self.transform_stmt(final_stmt))
            return transformed_stmts
        elif isinstance(stmt, ast.If):
            transformed_stmts = []
            for body_stmt in stmt.body:
                transformed_stmts.extend(self.transform_stmt(body_stmt))
            for orelse_stmt in stmt.orelse:
                transformed_stmts.extend(self.transform_stmt(orelse_stmt))
            return transformed_stmts
        elif isinstance(stmt, (ast.For, ast.AsyncFor)):
            transformed_stmts = []
            for body_stmt in stmt.body:
                transformed_stmts.extend(self.transform_stmt(body_stmt))
            return transformed_stmts
        elif isinstance(stmt, (ast.With, ast.AsyncWith)):
            transformed_stmts = []
            for body_stmt in stmt.body:
                transformed_stmts.extend(self.transform_stmt(body_stmt))
            return transformed_stmts
        elif isinstance(stmt, ast.With):
            transformed_stmts = []
            for body_stmt in stmt.body:
                transformed_stmts.extend(self.transform_stmt(body_stmt))
            return transformed_stmts
        elif isinstance(stmt, ast.Match):
            transformed_stmts = []
            for case in stmt.cases:
                for case_stmt in case.body:
                    transformed_stmts.extend(self.transform_stmt(case_stmt))
            return transformed_stmts
        else:
            return [stmt]

    def build_statements_list(self) -> list[AstStatement]:
        file_ast = build_ast(self.file.file_content)
        statement_list: list[AstStatement] = []

        for stmt_idx, stmt in enumerate(file_ast.body):
            transformed_stmts = self.transform_stmt(stmt)
            for transformed_stmt in transformed_stmts:
                statement_list.append(
                    AstStatement(
                        transformed_stmt,
                        len(statement_list),
                        self.file,
                        stmt,
                        stmt_idx,
                    )
                )
        return statement_list

    def build_var_to_stmt_idxs(self) -> dict[str, list[int]]:
        var_to_stmt_idxs: dict[str, list[int]] = defaultdict(list)
        for idx, stmt_obj in enumerate(self.statements_list):
            stmt = stmt_obj.stmt
            if isinstance(stmt, ast.Assign):
                for target in stmt.targets:
                    assigned_targets = AstStatements.assigned_expr_name_str(target)
                    if assigned_targets is not None:
                        for assigned_target in assigned_targets:
                            var_to_stmt_idxs[assigned_target].append(idx)
            elif isinstance(stmt, (ast.AugAssign, ast.AnnAssign)):
                assigned_target = AstStatements.assigned_expr_name_str(stmt.target)
                if assigned_target is not None:
                    var_to_stmt_idxs[assigned_target].append(idx)
            elif isinstance(
                stmt, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)
            ):
                assigned_target = stmt.name
                var_to_stmt_idxs[assigned_target].append(idx)
            elif isinstance(stmt, (ast.Import, ast.ImportFrom)):
                assert len(stmt.names) == 1, f"import - {ast.unparse(stmt)}"
                if stmt.names[0].name == "*":
                    continue
                assert stmt.names[0].asname is not None, f"import - {ast.unparse(stmt)}"

                assigned_target = stmt.names[0].asname
                var_to_stmt_idxs[assigned_target].append(idx)

        return var_to_stmt_idxs

    def find_wildcard_imports(self):
        wildcard_stmt_idxs: list[int] = []
        for idx, stmt_obj in enumerate(self.statements_list):
            stmt = stmt_obj.stmt
            if isinstance(stmt, ast.ImportFrom) and stmt.names[0].name == "*":
                wildcard_stmt_idxs.append(idx)
        return wildcard_stmt_idxs

    @staticmethod
    def assigned_expr_name_str(expr: ast.expr) -> list[str] | None:
        if isinstance(expr, ast.Name):
            return [expr.id]
        elif isinstance(expr, ast.Attribute):
            return AstStatements.assigned_expr_name_str(expr.value)
        elif isinstance(expr, ast.Subscript):
            return AstStatements.assigned_expr_name_str(expr.value)
        elif isinstance(expr, (ast.Tuple, ast.List)):
            assigned_names = []
            for el in expr.elts:
                assigned_name = AstStatements.assigned_expr_name_str(el)
                if assigned_name is not None:
                    assigned_names.extend(assigned_name)
            return assigned_names

        else:
            return None

    def resolve_last_stmt(
        self, global_var_name: str, current_stmt_idx: int | None = None
    ) -> AstStatement | None:
        """
        Resolves the last statement in the AstStatements file where
        the global variable (named global_var_name) is assigned.
        Optionally, you can provide the current statement index
        to start the search from in reverse order.
        """

        if current_stmt_idx is None:
            ## if None match any statement in the file
            start_idx = len(self.statements_list)
        else:
            ## otherwise match any till the current statement
            start_idx = current_stmt_idx

        global_var_indices = self.var_to_stmt_idxs.get(global_var_name, [])
        if len(global_var_indices) == 0:
            return None

        idx = bisect.bisect_left(global_var_indices, start_idx)

        if idx == 0:
            return None

        idx -= 1
        return self.statements_list[global_var_indices[idx]]

    def resolve_wildcard_imports(self) -> list[AstStatement]:
        resolved: list[AstStatement] = []
        for idx in self.wildcard_idxs:
            resolved.append(self.statements_list[idx])
        return resolved

    def find_function_stmt_with_name(self, function_name: str) -> AstStatement | None:
        for stmt_obj in self.statements_list:
            stmt = stmt_obj.stmt
            if (
                isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef))
                and stmt.name == function_name
            ):
                return stmt_obj
        return None

    def find_class_stmt_with_name(self, class_name: str) -> AstStatement | None:
        for stmt_obj in self.statements_list:
            stmt = stmt_obj.stmt
            if isinstance(stmt, ast.ClassDef) and stmt.name == class_name:
                return stmt_obj
        return None
