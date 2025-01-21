import ast

from r2e.pat.dependency_slicer.globals_finder.expr_globals import get_expr_globals
from r2e.pat.dependency_slicer.globals_finder.bytecode_globals import (
    get_funclass_globals,
)
from r2e.pat.dependency_slicer.globals_finder.type_annotation_globals import (
    astnode_to_type_annotation_globals,
)
from r2e.pat.dependency_slicer.globals_finder.defaultarg_globals import (
    get_defaultarg_globals,
)
from r2e.pat.dependency_slicer.globals_finder.decorator_globals import (
    get_decorator_globals,
)


def create_fake_function(node: ast.stmt):
    node_unparse = ast.unparse(node)
    wrapped_func_code = "def fake_func():\n"
    for line in node_unparse.split("\n"):
        wrapped_func_code += "    " + line + "\n"
    wrapped_func_node = ast.parse(wrapped_func_code).body[0]
    return wrapped_func_node


class StmtGlobalVariablesVisitor(ast.NodeVisitor):
    def visit(self, node) -> list[str]:
        if node is None:
            return []
        type_annotation_globals = astnode_to_type_annotation_globals(node)
        visit_super = super().visit(node)
        return visit_super + type_annotation_globals

    def visit_FunctionDef(self, node: ast.FunctionDef) -> list[str]:
        return self.definition_handler(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> list[str]:
        return self.definition_handler(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> list[str]:
        globals = self.definition_handler(node)
        for base in node.bases:
            globals += get_expr_globals(base)
        return globals

    def visit_Return(self, node: ast.Return) -> list[str]:
        return self.visit(node.value) if node.value else []

    def visit_Delete(self, node: ast.Delete) -> list[str]:
        globals: list[str] = []
        for target in node.targets:
            globals += get_expr_globals(target)
        return globals

    def visit_Assign(self, node: ast.Assign) -> list[str]:
        globals = []
        for target in node.targets:
            globals += get_expr_globals(target)
        globals += get_expr_globals(node.value)
        return globals

    # def visit_TypeAlias(self, node: ast.TypeAlias) -> list[str]:
    #     globals = get_expr_globals(node.name)
    #     globals += get_expr_globals(node.value)
    #     return globals

    def visit_AugAssign(self, node: ast.AugAssign) -> list[str]:
        globals = get_expr_globals(node.target)
        globals += get_expr_globals(node.value)
        return globals

    def visit_AnnAssign(self, node: ast.AnnAssign) -> list[str]:
        globals = get_expr_globals(node.annotation)
        if node.value:
            globals += get_expr_globals(node.value)
        return globals

    def visit_For(self, node: ast.For) -> list[str]:
        return self.for_handler(node)

    def visit_AsyncFor(self, node: ast.AsyncFor) -> list[str]:
        return self.for_handler(node)

    def visit_While(self, node: ast.While) -> list[str]:
        globals = get_expr_globals(node.test)
        for body_stmt in node.body:
            globals += get_stmt_globals(body_stmt)
        for if_condition in node.orelse:
            globals += get_stmt_globals(if_condition)
        return globals

    def visit_If(self, node: ast.If) -> list[str]:
        globals = get_expr_globals(node.test)
        for body_stmt in node.body:
            globals += get_stmt_globals(body_stmt)
        for if_condition in node.orelse:
            globals += get_stmt_globals(if_condition)
        return globals

    def visit_With(self, node: ast.With) -> list[str]:
        return self.with_handler(node)

    def visit_AsyncWith(self, node: ast.AsyncWith) -> list[str]:
        return self.with_handler(node)

    def visit_Match(self, node: ast.Match) -> list[str]:
        globals: list[str] = []
        for case in node.cases:
            globals += get_pattern_globals(case.pattern)
            if case.guard:
                globals += get_expr_globals(case.guard)
            for stmt in case.body:
                globals += get_stmt_globals(stmt)
        return globals

    def visit_Raise(self, node: ast.Raise) -> list[str]:
        globals = []
        if node.exc:
            globals += get_expr_globals(node.exc)
        if node.cause:
            globals += get_expr_globals(node.cause)
        return globals

    def visit_Try(self, node: ast.Try) -> list[str]:
        return self.try_handler(node)

    def visit_TryStar(self, node: ast.TryStar) -> list[str]:
        return self.try_handler(node)

    def visit_Assert(self, node: ast.Assert) -> list[str]:
        globals = get_expr_globals(node.test)
        if node.msg:
            globals += get_expr_globals(node.msg)
        return globals

    def visit_Import(self, node: ast.Import) -> list[str]:
        return []

    def visit_ImportFrom(self, node: ast.ImportFrom) -> list[str]:
        return []

    def visit_Global(self, node: ast.Global) -> list[str]:
        return node.names

    def visit_Nonlocal(self, node: ast.Nonlocal) -> list[str]:
        return node.names

    def visit_Expr(self, node: ast.Expr) -> list[str]:
        return get_expr_globals(node.value)

    def visit_Pass(self, node: ast.Pass) -> list[str]:
        return []

    def visit_Break(self, node: ast.Break) -> list[str]:
        return []

    def visit_Continue(self, node: ast.Continue) -> list[str]:
        return []

    def definition_handler(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef
    ) -> list[str]:
        all_globals: list[str] = []
        # def f(x=a): pass --> a is a global in the default value
        all_globals += get_defaultarg_globals(node)
        # @cache -> cache is a global
        all_globals += get_decorator_globals(node)
        # def f(): a=b --> b is a global in the body
        all_globals += get_funclass_globals(node)
        return all_globals

    def for_handler(self, node: ast.For | ast.AsyncFor) -> list[str]:
        return get_stmt_globals(create_fake_function(node))

    def with_handler(self, node: ast.With | ast.AsyncWith) -> list[str]:
        return get_stmt_globals(create_fake_function(node))

    def try_handler(self, node: ast.Try | ast.TryStar) -> list[str]:
        return get_stmt_globals(create_fake_function(node))


def get_stmt_globals(ast_node: ast.stmt) -> list[str]:
    visitor = StmtGlobalVariablesVisitor()
    return visitor.visit(ast_node)


def get_pattern_globals(pattern: ast.pattern) -> list[str]:
    # pattern = MatchValue(expr value)
    #     | MatchSingleton(constant value)
    #     | MatchSequence(pattern* patterns)
    #     | MatchMapping(expr* keys, pattern* patterns, identifier? rest)
    #     | MatchClass(expr cls, pattern* patterns, identifier* kwd_attrs, pattern* kwd_patterns)

    #     | MatchStar(identifier? name)
    #     -- The optional "rest" MatchMapping parameter handles capturing extra mapping keys

    #     | MatchAs(pattern? pattern, identifier? name)
    #     | MatchOr(pattern* patterns)

    if isinstance(pattern, ast.MatchValue):
        return get_expr_globals(pattern.value)
    elif isinstance(pattern, ast.MatchSingleton):
        return []
    elif isinstance(pattern, ast.MatchSequence):
        globals: list[str] = []
        for p in pattern.patterns:
            globals += get_pattern_globals(p)
        return globals
    elif isinstance(pattern, ast.MatchMapping):
        globals: list[str] = []
        for key in pattern.keys:
            globals += get_expr_globals(key)
        for p in pattern.patterns:
            globals += get_pattern_globals(p)
        if pattern.rest:
            globals.append(pattern.rest)
        return globals
    elif isinstance(pattern, ast.MatchClass):
        globals = get_expr_globals(pattern.cls)
        for p in pattern.patterns:
            globals += get_pattern_globals(p)
        for kwd_attr in pattern.kwd_attrs:
            globals.append(kwd_attr)
        for kwd_pattern in pattern.kwd_patterns:
            globals += get_pattern_globals(kwd_pattern)
        return globals
    elif isinstance(pattern, ast.MatchStar):
        return [pattern.name] if pattern.name else []
    elif isinstance(pattern, ast.MatchAs):
        globals: list[str] = []
        if pattern.pattern:
            globals += get_pattern_globals(pattern.pattern)
        if pattern.name:
            globals.append(pattern.name)
        return globals
    elif isinstance(pattern, ast.MatchOr):
        globals: list[str] = []
        for p in pattern.patterns:
            globals += get_pattern_globals(p)
        return globals
    return []


def get_excepthandler_globals(handler: ast.ExceptHandler) -> list[str]:
    globals: list[str] = []
    non_globals: list[str] = []
    if handler.name:
        non_globals.append(handler.name)

    for stmt in handler.body:
        globals += get_stmt_globals(stmt)
    globals = [g for g in globals if g not in non_globals]

    if handler.type:
        globals += get_expr_globals(handler.type)

    return globals
