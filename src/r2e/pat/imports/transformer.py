import ast
import os
import shutil
import importlib

from r2e.pat.modules.explorer import ModuleExplorer
from r2e.pat.imports.resolver import ImportResolver


class ImportTransformer:
    """Transforms imports in Python files."""

    @staticmethod
    def relative_to_absolute(file_path: str, node: ast.ImportFrom) -> None:
        """Converts relative imports to absolute imports."""
        module_parts = (node.module or "").split(".")
        package_name = ModuleExplorer.get_package_name(file_path)
        abs_parts = package_name.split(".") + module_parts[node.level - 1 :]
        node.module = ".".join(abs_parts).rstrip(".")
        node.level = 0

    @staticmethod
    def wildcard_to_explicit(file_path: str, node: ast.ImportFrom) -> None:
        """Converts wildcard imports to explicit imports."""
        module_file = ImportResolver.resolve_import_path(file_path, node)
        if os.path.exists(module_file):
            all_members = ModuleExplorer.get_member_names(module_file)
            node.names = [ast.alias(name=member, asname=None) for member in all_members]

        # attempt to resolve external library
        else:
            try:
                module = importlib.import_module(node.module)  # type: ignore
                all_members = [name for name in dir(module) if not name.startswith("_")]
                if hasattr(module, "__all__"):
                    all_members = [
                        name for name in all_members if name in module.__all__
                    ]
                node.names = [
                    ast.alias(name=member, asname=None) for member in all_members
                ]
            except ImportError:
                pass

    @staticmethod
    def transform_import(file_path: str, node: ast.ImportFrom) -> None:
        """Applies various transformations to an import statement in a Python file."""
        if isinstance(node, ast.ImportFrom):
            if node.level > 0:
                ImportTransformer.relative_to_absolute(file_path, node)

            if node.names[0].name == "*":
                ImportTransformer.wildcard_to_explicit(file_path, node)

    @staticmethod
    def transform_file(file_path: str) -> None:
        """Applies various transformations to all imports in a Python file."""
        with open(file_path, "r") as file:
            try:
                tree = ast.parse(file.read())
            except SyntaxError:
                raise SyntaxError(f"Syntax error in file: {file_path}")

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                ImportTransformer.transform_import(file_path, node)

        source_code = ast.unparse(tree)
        ast.parse(source_code)
        with open(file_path, "w") as file:
            file.write(source_code)

    @staticmethod
    def transform_repo(repo_path: str) -> str:
        """Applies various transformations to all imports in a Python repository."""
        temp_path = repo_path + "_temp"
        if os.path.exists(temp_path):
            shutil.rmtree(temp_path)
        temp_path = shutil.copytree(repo_path, temp_path)

        for root, _, files in os.walk(temp_path):
            for file in files:
                if file.endswith(".py"):
                    try:
                        ImportTransformer.transform_file(os.path.join(root, file))
                    except SyntaxError as e:
                        print(f"Error in file: {os.path.join(root, file)}")
                        print(e)
                        raise e
        return temp_path
