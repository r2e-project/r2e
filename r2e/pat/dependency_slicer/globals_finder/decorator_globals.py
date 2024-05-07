import ast

from r2e.pat.dependency_slicer.globals_finder.expr_globals import get_expr_globals


def get_decorator_globals(
    astnode: ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef,
) -> list[str]:
    """
    Find all the global symbols in the ast node
    Further filters builtins and non-dependency globals
    :param astnode: ast.AST
    :return: list[str] - list of global symbols
    """
    all_decorator_globals = []
    for node in ast.walk(astnode):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            for decorator in node.decorator_list:
                unparsed_decorator = ast.unparse(decorator)
                if ".setter" in unparsed_decorator:
                    continue
                if ".getter" in unparsed_decorator:
                    continue
                if ".deleter" in unparsed_decorator:
                    continue
                if ".wraps" in unparsed_decorator:
                    continue
                all_decorator_globals.extend(get_expr_globals(decorator))
    return all_decorator_globals
