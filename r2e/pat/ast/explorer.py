"""Python AST builder and explorer."""

import ast
from typed_ast import ast27
from typing import Optional

from r2e.pat.ast.augmenter import add_parent_info

def build_ast(code: str, add_parents: bool = True) -> ast.Module:
    """Build an AST from a code snippet.

    Args:
        code (str): the code snippet

    Returns:
        ast.AST: the AST
    """
    try:
        astree = ast.parse(code)
    except:
        try:
            astree = ast27.parse(code)
        except:
            print(f"WARNING: Python3 and Python2 parsers both failed on code {code}")
        finally:
            #print("Had to use Python2 parser")
            pass
    if add_parents:
        astree = add_parent_info(astree)
    return astree


def build_ast_file(file_path: str, add_parents: bool = True) -> ast.Module:
    """Build an AST from a file.

    Args:
        file_path (str): the file path

    Returns:
        ast.AST: the AST
    """
    with open(file_path, "r") as f:
        code = f.read()
    return build_ast(code, add_parents=add_parents)


def find_def_in_ast(
    astree: ast.AST, name: str, def_type: Optional[type | tuple[type, ...]] = None
) -> Optional[ast.AST]:
    """Find the first definition of a function/class in an AST.

    Args:
        astree (ast.AST): the AST to search
        name (str): the name of the definition

    Returns:
        ast.AST: the definition node
    """

    definition_types = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
    if def_type is not None:
        definition_types = def_type if isinstance(def_type, tuple) else (def_type,)

    for node in ast.walk(astree):
        if isinstance(
            node,
            definition_types,
        ):
            node_name = getattr(node, "name", None)
            if node_name == name:
                return node

    return None


def find_function_in_ast(
    astree: ast.AST, name: str
) -> Optional[ast.FunctionDef | ast.AsyncFunctionDef]:
    """Find a function definition in an AST.

    Args:
        astree (ast.AST): the AST to search
        name (str): the name of the function

    Returns:
        Optional[ast.FunctionDef]: the function definition node
    """
    func_def_types = (ast.FunctionDef, ast.AsyncFunctionDef)
    found_node = find_def_in_ast(astree, name, func_def_types)
    return found_node if isinstance(found_node, func_def_types) else None


def body_import_finder(
    node: ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef,
) -> list[ast.Import | ast.ImportFrom]:
    all_imports: list[ast.Import | ast.ImportFrom] = []
    for stmt in node.body:
        if isinstance(stmt, (ast.Import, ast.ImportFrom)):
            all_imports.append(stmt)
        if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            all_imports += body_import_finder(stmt)
    return all_imports
