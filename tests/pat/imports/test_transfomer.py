import ast
import os
import tempfile
import unittest

from r2e.pat.imports.transformer import ImportTransformer


class TestImportTransformer(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.package_dir = os.path.join(self.temp_dir.name, "mypackage")
        os.makedirs(self.package_dir)

        # make it a package
        with open(os.path.join(self.package_dir, "__init__.py"), "w") as f:
            f.write("# Package init file")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_transform_import(self):
        """
        temp_dir/
        └── mypackage/
            ├── __init__.py
            ├── submodule.py
            └── test_file.py
               from .submodule import *
        """

        submodule_path = os.path.join(self.package_dir, "submodule.py")
        with open(submodule_path, "w") as f:
            file_content = """
def some_function():
    return 'Hello, World!'

class SomeClass:
    pass
"""
            f.write(file_content)

        test_file_path = os.path.join(self.package_dir, "test_file.py")
        with open(test_file_path, "w") as f:
            f.write("from .submodule import *")

        with open(test_file_path, "r") as f:
            tree = ast.parse(f.read())
        import_node = next(
            node for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)
        )

        ImportTransformer.transform_import(test_file_path, import_node)
        self.assertEqual(import_node.module, "mypackage.submodule")
        self.assertEqual(import_node.level, 0)
        self.assertEqual(len(import_node.names), 2)
        self.assertEqual(import_node.names[0].name, "some_function")
        self.assertEqual(import_node.names[0].asname, None)
        self.assertEqual(import_node.names[1].name, "SomeClass")
        self.assertEqual(import_node.names[1].asname, None)

    def test_transform_library_wildcard(self):
        """
        temp_dir/
        └── mypackage/
            ├── __init__.py
            └── test_file.py
               from ctypes.wintypes import *
        """

        test_file_path = os.path.join(self.package_dir, "test_file.py")
        with open(test_file_path, "w") as f:
            f.write("from ctypes.wintypes import *")

        with open(test_file_path, "r") as f:
            tree = ast.parse(f.read())
        import_node = next(
            node for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)
        )

        ImportTransformer.transform_import(test_file_path, import_node)
        self.assertEqual(import_node.module, "ctypes.wintypes")
        self.assertEqual(import_node.level, 0)
        self.assertTrue(any(alias.name == "BOOLEAN" for alias in import_node.names))
        self.assertTrue(any(alias.name == "ULONG" for alias in import_node.names))


if __name__ == "__main__":
    unittest.main()
