import ast

from r2e.pat.dependency_slicer.globals_finder.expr_globals import get_expr_globals


def collect_arg_defaults(
    astnode: ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef,
) -> list[ast.expr]:
    """
    extract all the default arguments from a function or class
    this will also recursively parse default for nested functions, classes, and methods
    :param astnode: ast.FunctionDef | ast.ClassDef
    :return: list[ast.AST] - list of default argument AST nodes
    """
    all_default_asts: list[ast.expr] = []
    for node in ast.walk(astnode):
        if isinstance(node, ast.arguments):
            all_default_asts.extend(node.defaults)
            all_default_asts.extend([expr for expr in node.kw_defaults if expr])
    return all_default_asts


def defaults_to_globals(default_asts: list[ast.expr]) -> list[str]:
    """
    parse all the global variables from the default arguments
    maps ast type and corresponding global variable appropriately
    :param defaults: list[ast.AST] - list of default argument AST nodes
    :return: list[str] - list of global variables
    """

    global_vars = []
    for default_ast in default_asts:
        global_vars.extend(get_expr_globals(default_ast))
    return global_vars


def get_defaultarg_globals(
    astnode: ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef,
) -> list[str]:
    """
    extract all the global variables from the default arguments of a function or class
    :param astnode: ast.FunctionDef | ast.ClassDef
    :return: list[str] - list of global variables
    """
    default_asts = collect_arg_defaults(astnode)
    return defaults_to_globals(default_asts)
