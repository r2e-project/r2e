import ast
import os
import shutil
import tempfile
import unittest

from r2e.pat.imports.resolver import ImportResolver


class TestImportResolver(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def add_my_package(self):
        self.package_dir = os.path.join(self.temp_dir.name, "mypackage")
        os.makedirs(self.package_dir)
        with open(os.path.join(self.package_dir, "__init__.py"), "w") as f:
            f.write("# Package init file")

    def test_absolute_import_module_item(self):
        """
        temp_dir/
        └── mypackage/
            ├── __init__.py
            ├── submodule.py
            └── test_file.py
               from mypackage.submodule import some_function
        """
        self.add_my_package()
        submodule_path = os.path.join(self.package_dir, "submodule.py")
        with open(submodule_path, "w") as f:
            f.write("def some_function():\n    return 'Hello, World!'")

        test_file_path = os.path.join(self.package_dir, "test_file.py")
        with open(test_file_path, "w") as f:
            f.write("from mypackage.submodule import some_function")

        with open(test_file_path, "r") as f:
            tree = ast.parse(f.read())
        import_node = next(
            node for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)
        )
        resolved_path = ImportResolver.resolve_import_path(test_file_path, import_node)
        expected_path = os.path.join(self.package_dir, "submodule.py")
        self.assertEqual(resolved_path, expected_path)

    def test_relative_import_module_item(self):
        """
        temp_dir/
        └── mypackage/
            ├── __init__.py
            ├── submodule.py
            └── subpackage/
                ├── __init__.py
                └── test_file.py
                    from ..submodule import some_function
        """
        self.add_my_package()
        submodule_path = os.path.join(self.package_dir, "submodule.py")
        with open(submodule_path, "w") as f:
            f.write("def some_function():\n    return 'Hello, World!'")

        subpackage_dir = os.path.join(self.package_dir, "subpackage")
        os.makedirs(subpackage_dir)
        with open(os.path.join(subpackage_dir, "__init__.py"), "w") as f:
            f.write("# Subpackage init file")

        test_file_path = os.path.join(subpackage_dir, "test_file.py")
        with open(test_file_path, "w") as f:
            f.write("from ..submodule import some_function")

        with open(test_file_path, "r") as f:
            tree = ast.parse(f.read())
        import_node = next(
            node for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)
        )
        resolved_path = ImportResolver.resolve_import_path(test_file_path, import_node)
        expected_path = os.path.join(self.package_dir, "submodule.py")
        self.assertEqual(resolved_path, expected_path)

    def test_relative_import_across_packages(self):
        """
        temp_dir/
        ├── package1/
        │   ├── __init__.py
        │   └── module1.py
        │       from ..package2.module2 import some_function
        └── package2/
            ├── __init__.py
            └── module2.py
                def some_function():
                    return 'Hello, World!'
        """
        package1_dir = os.path.join(self.temp_dir.name, "package1")
        os.makedirs(package1_dir)
        with open(os.path.join(package1_dir, "__init__.py"), "w") as f:
            f.write("# Package1 init file")

        module1_path = os.path.join(package1_dir, "module1.py")
        with open(module1_path, "w") as f:
            f.write("from ..package2.module2 import some_function")

        package2_dir = os.path.join(self.temp_dir.name, "package2")
        os.makedirs(package2_dir)
        with open(os.path.join(package2_dir, "__init__.py"), "w") as f:
            f.write("# Package2 init file")

        module2_path = os.path.join(package2_dir, "module2.py")
        with open(module2_path, "w") as f:
            f.write("def some_function():\n    return 'Hello, World!'")

        with open(module1_path, "r") as f:
            tree = ast.parse(f.read())
        import_node = next(
            node for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)
        )
        resolved_path = ImportResolver.resolve_import_path(module1_path, import_node)
        expected_path = os.path.join(package2_dir, "module2.py")
        self.assertEqual(resolved_path, expected_path)

    def test_relative_import_package_in_repo(self):
        """
        temp_dir/
        └── anticipation
            ├── anticipation
                ├── __init__.py
                ├── config.py
                └── sample.py
                from anticipation.config import *
        """

        anticipation_dir = os.path.join(self.temp_dir.name, "anticipation")
        os.makedirs(anticipation_dir)
        anticipation_pkg_dir = os.path.join(anticipation_dir, "anticipation")
        os.makedirs(anticipation_pkg_dir)
        with open(os.path.join(anticipation_pkg_dir, "__init__.py"), "w") as f:
            f.write("# Anticipation package init file")
        with open(os.path.join(anticipation_pkg_dir, "config.py"), "w") as f:
            f.write("# Anticipation config file")
        with open(os.path.join(anticipation_pkg_dir, "sample.py"), "w") as f:
            f.write("from anticipation.config import *")

        sample_path = os.path.join(anticipation_pkg_dir, "sample.py")
        with open(sample_path, "r") as f:
            tree = ast.parse(f.read())
        import_node = next(
            node for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)
        )
        resolved_path = ImportResolver.resolve_import_path(sample_path, import_node)
        expected_path = os.path.join(anticipation_pkg_dir, "config.py")
        self.assertEqual(resolved_path, expected_path)

    def test_absolute_import_src_in_repo(self):
        """
        temp_dir/
        └── pyastgrep
            ├── pyproject.toml
            ├── src
                ├── pyastgrep
                    ├── __init__.py
                    ├── search.py
                    └── color.py
                    from pyastgrep.search import Match
        """

        pyastgrep_dir = os.path.join(self.temp_dir.name, "pyastgrep")
        os.makedirs(pyastgrep_dir)
        pyastgrep_src_dir = os.path.join(pyastgrep_dir, "src")
        os.makedirs(pyastgrep_src_dir)
        pyastgrep_pkg_dir = os.path.join(pyastgrep_src_dir, "pyastgrep")
        os.makedirs(pyastgrep_pkg_dir)
        with open(os.path.join(pyastgrep_pkg_dir, "__init__.py"), "w") as f:
            f.write("# Pyastgrep package init file")
        with open(os.path.join(pyastgrep_pkg_dir, "search.py"), "w") as f:
            f.write("# Pyastgrep search file")
        color_path = os.path.join(pyastgrep_pkg_dir, "color.py")
        with open(color_path, "w") as f:
            f.write("from pyastgrep.search import Match")

        with open(color_path, "r") as f:
            tree = ast.parse(f.read())
        import_node = next(
            node for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)
        )
        resolved_path = ImportResolver.resolve_import_path(color_path, import_node)
        expected_path = os.path.join(pyastgrep_pkg_dir, "search.py")
        self.assertEqual(resolved_path, expected_path)

    def test_absolute_import_nested_in_src_in_repo(self):
        """
        temp_dir/
        └── pyastgrep
            ├── pyproject.toml
            ├── src
                ├── pyastgrep
                    ├── __init__.py
                    ├── search.py
                    └── color
                        ├── __init__.py
                        └── color.py
                        from pyastgrep.search import Match
        """

        pyastgrep_dir = os.path.join(self.temp_dir.name, "pyastgrep")
        os.makedirs(pyastgrep_dir)
        pyastgrep_src_dir = os.path.join(pyastgrep_dir, "src")
        os.makedirs(pyastgrep_src_dir)
        pyastgrep_pkg_dir = os.path.join(pyastgrep_src_dir, "pyastgrep")
        os.makedirs(pyastgrep_pkg_dir)
        with open(os.path.join(pyastgrep_pkg_dir, "__init__.py"), "w") as f:
            f.write("# Pyastgrep package init file")
        with open(os.path.join(pyastgrep_pkg_dir, "search.py"), "w") as f:
            f.write("# Pyastgrep search file")
        color_dir = os.path.join(pyastgrep_pkg_dir, "color")
        os.makedirs(color_dir)
        with open(os.path.join(color_dir, "__init__.py"), "w") as f:
            f.write("# Color package init file")
        color_path = os.path.join(color_dir, "color.py")
        with open(color_path, "w") as f:
            f.write("from pyastgrep.search import Match")

        with open(color_path, "r") as f:
            tree = ast.parse(f.read())
        import_node = next(
            node for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)
        )

        resolved_path = ImportResolver.resolve_import_path(color_path, import_node)
        expected_path = os.path.join(pyastgrep_pkg_dir, "search.py")
        self.assertEqual(resolved_path, expected_path)

    def test_relative_import_package(self):
        """
        temp_dir/
        └── test_package/
            ├── __init__.py
            └── test_file.py
                from . import test_package
        """
        test_package_dir = os.path.join(self.temp_dir.name, "test_package")
        os.makedirs(test_package_dir)
        with open(os.path.join(test_package_dir, "__init__.py"), "w") as f:
            f.write("# Package init file")

        test_file_path = os.path.join(test_package_dir, "test_file.py")
        with open(test_file_path, "w") as f:
            f.write("from . import test_package")

        with open(test_file_path, "r") as f:
            tree = ast.parse(f.read())
        import_node = next(
            node for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)
        )

        # Resolve the import path
        resolved_path = ImportResolver.resolve_import_path(test_file_path, import_node)
        expected_path = os.path.join(test_package_dir, "__init__.py")
        self.assertEqual(resolved_path, expected_path)

    def test_import_package_as_module(self):
        """
        temp_dir/
        └── mypackage/
            ├── __init__.py
            └── test_file.py
                import mypackage
        """
        self.add_my_package()
        with open(os.path.join(self.package_dir, "__init__.py"), "w") as f:
            f.write("# Package init file")

        test_file_path = os.path.join(self.package_dir, "test_file.py")
        with open(test_file_path, "w") as f:
            f.write("import mypackage")

        with open(test_file_path, "r") as f:
            tree = ast.parse(f.read())
        import_node = next(
            node for node in ast.walk(tree) if isinstance(node, ast.Import)
        )

        resolved_path = ImportResolver.resolve_import_path(test_file_path, import_node)
        expected_path = os.path.join(self.package_dir, "__init__.py")
        self.assertEqual(resolved_path, expected_path)

    def test_absolute_import_from_subpackage(self):
        """
        temp_dir/
        └── pyastgrep
            ├── pyproject.toml
            ├── src
                ├── pyastgrep
                    ├── __init__.py
                    ├── search.py
                    └── color
                        ├── __init__.py
                        └── color.py
                            from color.color2.colorme import Bar
                        └── color2
                            ├── __init__.py
                            └── colorme.py
        """

        pyastgrep_dir = os.path.join(self.temp_dir.name, "pyastgrep")
        os.makedirs(pyastgrep_dir)
        pyastgrep_src_dir = os.path.join(pyastgrep_dir, "src")
        os.makedirs(pyastgrep_src_dir)
        pyastgrep_pkg_dir = os.path.join(pyastgrep_src_dir, "pyastgrep")
        os.makedirs(pyastgrep_pkg_dir)
        with open(os.path.join(pyastgrep_pkg_dir, "__init__.py"), "w") as f:
            f.write("# Pyastgrep package init file")
        with open(os.path.join(pyastgrep_pkg_dir, "search.py"), "w") as f:
            f.write("# Pyastgrep search file")
        color_dir = os.path.join(pyastgrep_pkg_dir, "color")
        os.makedirs(color_dir)
        with open(os.path.join(color_dir, "__init__.py"), "w") as f:
            f.write("# Color package init file")
        color2_dir = os.path.join(color_dir, "color2")
        os.makedirs(color2_dir)

        with open(os.path.join(color2_dir, "__init__.py"), "w") as f:
            f.write("# color2 package init file")
        with open(os.path.join(color2_dir, "colorme.py"), "w") as f:
            f.write("# Color2 colorme file")

        color_path = os.path.join(color_dir, "color.py")
        with open(color_path, "w") as f:
            f.write(
                "from color2.colorme import Bar\nfrom pyastgrep.search import Match"
            )

        with open(color_path, "r") as f:
            tree = ast.parse(f.read())
        import_node = next(
            node for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)
        )

        resolved_path = ImportResolver.resolve_import_path(color_path, import_node)
        expected_path = os.path.join(color2_dir, "colorme.py")
        self.assertEqual(resolved_path, expected_path)


if __name__ == "__main__":
    unittest.main()
