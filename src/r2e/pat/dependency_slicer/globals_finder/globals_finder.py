import ast
import builtins

from r2e.pat.dependency_slicer.globals_finder.type_annotation_globals import (
    astnode_to_type_annotation_globals,
)
from r2e.pat.dependency_slicer.globals_finder.bytecode_globals import (
    get_funclass_globals,
)


def create_fake_function(node: ast.stmt) -> ast.AsyncFunctionDef:
    node_unparse = ast.unparse(node)
    wrapped_func_code = "async def fake_func():\n"
    for line in node_unparse.split("\n"):
        wrapped_func_code += "    " + line + "\n"
    wrapped_func_node = ast.parse(wrapped_func_code).body[0]
    return wrapped_func_node  # type: ignore


def find_dependency_globals(astnode: ast.stmt, unique: bool = True) -> list[str]:
    """
    Find all the global symbols in the ast node
    Further filters builtins and non-dependency globals
    :param astnode: ast.AST
    :return: list[str] - list of global symbols
    """

    fake_function_node = create_fake_function(astnode)

    all_type_annotation_globals = astnode_to_type_annotation_globals(astnode)

    all_globals = get_funclass_globals(fake_function_node)

    all_globals.extend(all_type_annotation_globals)

    # filter out builtins
    all_globals = [g for g in all_globals if g not in dir(builtins)]

    # filter __name__, __file__, __str__ etc
    all_globals = [
        g for g in all_globals if not (g.startswith("__") and g.endswith("__"))
    ]

    if unique:
        return list(set(all_globals))

    return all_globals
