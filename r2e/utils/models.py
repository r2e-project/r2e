import os
import ast
from typing import Any
import typing_extensions

from r2e.models.identifier import Identifier
from r2e.models.module import Module
from r2e.models.repo import Repo
from r2e.models.callgraph import CodeElemType
from r2e.pat.ast.explorer import build_ast_file
from r2e.paths import BUCKET_DIR


IncEx: typing_extensions.TypeAlias = (
    "set[int] | set[str] | dict[int, Any] | dict[str, Any] | None"
)


def get_module_from_identifier(identifier: Identifier, repo: Repo) -> Module:
    """Get the module of a code element given the identifier and repo.

    NOTE: use this when a code element of identifier `identifier`
    has not yet been created; hence the module is not yet available.
    otherwise, something like `code_elem.module` should be used.

    Args:
        identifier (Identifier): identifier of the code element in repo
        repo (Repo): repository of interest

    Raises:
        ValueError: if the module of the code element is not found

    Returns:
        Module: module of the code element
    """
    func_or_class_module = create_func_or_class_module(identifier, repo)
    meth_module = create_method_module(identifier, repo)

    if func_or_class_module.exists():
        return func_or_class_module
    elif meth_module.exists():
        return meth_module
    else:
        raise ValueError(f"Could not find module for: {identifier}")


def get_module_from_path(local_path: str, repo: Repo) -> Module:
    """
    Gets the module from a local path in a repo.

    Args:
        local_path (str): local path of the module
        repo (Repo): repository of interest

    Returns:
        Module: module of the code element
    """
    relative_path = local_path.split(f"{repo.local_repo_path}/")[1]
    module_id = Identifier.from_relative_path(relative_path)
    module = Module(module_id=module_id, repo=repo)
    return module


def get_type_from_identifier(identifier: Identifier, repo: Repo) -> CodeElemType:
    """Get the type of a code element given its identifier.

    Args:
        identifier (Identifier): identifier of the code element

    Returns:
        CodeElemType: type of the code element
    """

    if identifier.identifier.startswith("<builtin>"):
        return CodeElemType.BUILTIN

    func_or_class_module = create_func_or_class_module(identifier, repo)
    meth_module = create_method_module(identifier, repo)

    if func_or_class_module.exists():
        file_ast = build_ast_file(func_or_class_module.local_path)
        code_elem_name = identifier.identifier.split(".")[-1]

        for node in file_ast.body:  # type: ignore
            if (
                isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                and node.name == code_elem_name
            ):
                return CodeElemType.FUNCTION
            elif isinstance(node, ast.ClassDef) and node.name == code_elem_name:
                return CodeElemType.CLASS

        return CodeElemType.OTHER

    elif meth_module.exists():
        file_ast = build_ast_file(meth_module.local_path)
        code_elem_name = identifier.identifier.split(".")[-1]
        code_elem_parent = identifier.identifier.split(".")[-2]

        for node in file_ast.body:  # type: ignore
            if isinstance(node, ast.ClassDef) and node.name == code_elem_parent:
                for n in node.body:
                    if (
                        isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                        and n.name == code_elem_name
                    ):
                        return CodeElemType.METHOD

        return CodeElemType.OTHER

    else:
        first_part = identifier.identifier.split(".")[0]
        paths_in_repo = []
        for root, dirs, files in os.walk(f"{BUCKET_DIR}/{repo.local_repo_path}/"):
            for file in files:
                if file.endswith(".py"):
                    paths_in_repo.append(os.path.join(root, file))

        if not any(first_part in path for path in paths_in_repo):
            return CodeElemType.API

        return CodeElemType.OTHER


def create_func_or_class_module(identifier: Identifier, repo: Repo) -> Module:
    """Create a module for a function or class given its identifier and repo."""
    mod_from_func_class = lambda item: ".".join(item.split(".")[:-1])
    func_module_id = Identifier(identifier=mod_from_func_class(identifier.identifier))
    func_module = Module(module_id=func_module_id, repo=repo)

    return func_module


def create_method_module(identifier: Identifier, repo: Repo) -> Module:
    """Create a module for a method given its identifier and repo."""
    mod_from_method = lambda item: ".".join(item.split(".")[:-2])
    meth_module_id = Identifier(identifier=mod_from_method(identifier.identifier))
    meth_module = Module(module_id=meth_module_id, repo=repo)

    return meth_module


def update_exclude_fields(exclude: IncEx, fields_to_exclude: set[str]) -> IncEx:
    """Update exclude set with fields to exclude.

    Args:
        exclude (IncEx): exclude set of a model
        fields_to_exclude (set[str]): fields to exclude

    Raises:
        ValueError: if exclude is not None, a set, or a dict

    Returns:
        IncEx: updated exclude set
    """
    if exclude is None:
        exclude = fields_to_exclude
    elif isinstance(exclude, set):
        exclude |= fields_to_exclude  # type: ignore
    elif isinstance(exclude, dict):
        for field in fields_to_exclude:
            exclude[field] = ...  # type: ignore
    else:
        raise ValueError("exclude must be None, a set, or a dict")
    return exclude
