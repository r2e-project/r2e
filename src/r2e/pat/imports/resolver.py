import ast
import os

from r2e.pat.modules.explorer import ModuleExplorer


class ImportResolver:
    """Resolves file paths for import statements."""

    @staticmethod
    def resolve_import_path(file_path: str, node: ast.ImportFrom | ast.Import) -> str:
        """Resolves the absolute file path of an import statement.

        Args:
            file_path (str): Path to the Python file containing the import.
            node (ast.ImportFrom | ast.Import): The import statement node.

        Returns:
            str: The resolved absolute file path.
        """
        if isinstance(node, ast.ImportFrom):
            module_parts = (node.module or "").split(".")
            level = node.level
        elif isinstance(node, ast.Import):
            if not node.names:
                raise ValueError("No module name found in import statement.")
            module_parts = node.names[0].name.split(".")
            level = 0
        else:
            raise ValueError("Unsupported import node type.")

        base_dir = os.path.dirname(file_path)
        root_dir = ModuleExplorer.get_package_root(file_path)
        resolved_path = None

        if level > 0:
            resolved_path = ImportResolver.resolve_relative_import(
                base_dir, module_parts, level
            )
        else:
            resolved_path = ImportResolver.resolve_absolute_import(
                base_dir, root_dir, module_parts
            )

        if os.path.isdir(os.path.abspath(resolved_path)):
            package_path = os.path.join(resolved_path, "__init__.py")
            return os.path.abspath(package_path)
        else:
            return os.path.abspath(resolved_path + ".py")

    # helper functions

    @staticmethod
    def resolve_absolute_import(
        base_dir: str, root_dir: str, module_parts: list[str]
    ) -> str:

        def potential_path_exists(path: str) -> bool:
            return os.path.exists(path) or os.path.exists(path + ".py")

        # type 1: absolute import from top-level package (root_dir)
        resolved_path = os.path.join(root_dir, *module_parts)
        if potential_path_exists(resolved_path):
            return resolved_path

        # type 2: absolute import from subpackage at current level (base_dir)
        resolved_path = os.path.join(base_dir, *module_parts)
        if potential_path_exists(resolved_path):
            return resolved_path

        # type 3: absolute import from subpackage at any level
        current_dir = base_dir
        while current_dir.startswith(root_dir):
            potential_path = os.path.join(current_dir, *module_parts)

            if potential_path_exists(potential_path):
                return potential_path

            current_dir = os.path.dirname(current_dir)

        # default: type 1
        return os.path.join(root_dir, *module_parts)

    @staticmethod
    def resolve_relative_import(
        base_dir: str, module_parts: list[str], level: int
    ) -> str:
        return os.path.join(base_dir, *[".."] * (level - 1), *module_parts)
