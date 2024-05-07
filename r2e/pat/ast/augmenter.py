"""Python AST augmentation tools."""

import ast
from typing import TypeVar

T = TypeVar("T", bound=ast.AST)


def add_parent_info(tree: T) -> T:
    """Add parent information to each node in the AST.

    Args:
        tree (ast.AST): the AST

    Returns:
        ast.AST: the AST with parent information
    """
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            setattr(child, "parent", node)
    setattr(tree, "parent", None)
    return tree
