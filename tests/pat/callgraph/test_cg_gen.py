import os
import unittest
import tempfile

from r2e.pat.callgraph.generator import CallGraphGenerator


class TestCallGraphGenerator(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.repo_path = self.test_dir.name
        os.makedirs(os.path.join(self.repo_path, "module"), exist_ok=True)

        with open(os.path.join(self.repo_path, "module", "__init__.py"), "w") as f:
            f.write("")

        with open(os.path.join(self.repo_path, "module", "utils.py"), "w") as f:
            f.write(
                """
def helper():
    print("Helper function")

class Utils:
    def compute(self, x):
        return x * x
"""
            )

        with open(os.path.join(self.repo_path, "module", "more_utils.py"), "w") as f:
            f.write(
                """
from .utils import Utils

def advanced_helper():
    util_instance = Utils()
    return util_instance.compute(5)
"""
            )

        with open(os.path.join(self.repo_path, "test.py"), "w") as f:
            f.write(
                """
from module.utils import helper
from module.more_utils import advanced_helper

def foo():
    helper()
    result = advanced_helper()
    print(result)

class TestClass:
    def method_one(self):
        foo()

    def method_two(self):
        self.method_one()

if __name__ == "__main__":
    test_instance = TestClass()
    test_instance.method_two()
"""
            )

    def tearDown(self):
        self.test_dir.cleanup()

    def test_construct_call_graph(self):
        cgraph = CallGraphGenerator.construct_call_graph(self.repo_path)
        expected_graph = {
            "test": [
                "test.TestClass.method_two",
            ],
            "test.foo": [
                "module.utils.helper",
                "module.more_utils.advanced_helper",
                "<builtin>.print",
            ],
            "test.TestClass.method_one": ["test.foo"],
            "test.TestClass.method_two": ["test.TestClass.method_one"],
            "module.utils.helper": ["<builtin>.print"],
            "module.utils.Utils.compute": [],
            "module.more_utils.advanced_helper": ["module.utils.Utils.compute"],
        }

        for key in expected_graph:
            self.assertIn(key, cgraph)
            self.assertEqual(sorted(expected_graph[key]), sorted(cgraph[key]))


if __name__ == "__main__":
    unittest.main()
