import json
import os
import unittest
from unittest.mock import patch, mock_open
import tempfile

from r2e.models.identifier import Identifier
from r2e.models.module import Module
from r2e.models.repo import Repo
from r2e.models.function import Function
from r2e.models.method import Method
from r2e.models.classes import Class


from r2e.models.file import File
from r2e.models.callgraph import CallGraph

from r2e.pat.callgraph.explorer import CallGraphExplorer


callgraph_json = json.dumps(
    {
        "graph": {
            "src.utils.foo": ["src.utils.bar"],
            "src.classes.MyClass": ["<builtin>.print"],
            "src.classes.MyClass.my_method": ["src.utils.baz"],
            "src.classes.MyClass.my_method2": ["src.classes.MyClass.my_method"],
        },
        "id2type": {
            "src.utils.foo": "FUNCTION",
            "src.utils.bar": "FUNCTION",
            "src.utils.baz": "FUNCTION",
            "src.classes.MyClass": "CLASS",
            "src.classes.MyClass.my_method": "METHOD",
            "src.classes.MyClass.my_method2": "METHOD",
            "<builtin>.print": "BUILTIN",
        },
    }
)


class TestCallGraphExplorer(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.repo_path = self.test_dir.name

        self.repo = Repo(
            repo_org="",
            repo_name="test_repo",
            repo_id="",
            local_repo_path=self.repo_path,
        )

    def tearDown(self):
        self.test_dir.cleanup()

    @patch("os.path.exists", return_value=True)
    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data=callgraph_json,
    )
    def test_get_function_callees(self, mock_open, mock_exists):
        cg_explorer = CallGraphExplorer(self.repo)
        callees = cg_explorer.get_callees_from_identifier("src.utils.foo")
        self.assertEqual(len(callees), 1)
        self.assertIsInstance(callees[0], Function)

        if isinstance(callees[0], Function):
            self.assertEqual(callees[0].function_id.identifier, "src.utils.bar")

    @patch("os.path.exists", return_value=True)
    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data=callgraph_json,
    )
    def test_get_class_method_callees(self, mock_open, mock_exists):
        cg_explorer = CallGraphExplorer(self.repo)
        callees = cg_explorer.get_callees_from_identifier(
            "src.classes.MyClass.my_method2"
        )
        self.assertEqual(len(callees), 1)
        self.assertIsInstance(callees[0], Method)

        if isinstance(callees[0], Method):
            self.assertEqual(
                callees[0].method_id.identifier, "src.classes.MyClass.my_method"
            )

        # check if the caller and callee have the same parent class attribute
        caller_id = Identifier(identifier="src.classes.MyClass.my_method")
        caller = Method.from_id_and_repo(caller_id, self.repo)

        if isinstance(callees[0], Method):
            self.assertEqual(callees[0].parent_class_id, caller.parent_class_id)

        # check if both caller and callee are methods of the parent class
        class_id = Identifier(identifier="src.classes.MyClass")
        class_ = Class.from_id_and_repo(class_id, self.repo)
        class_methods_ids = class_.method_ids
        self.assertIn(caller.method_id, class_methods_ids)

        if isinstance(callees[0], Method):
            self.assertIn(callees[0].method_id, class_methods_ids)

    @patch("os.path.exists", return_value=True)
    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data=callgraph_json,
    )
    def test_get_class_callees(self, mock_open, mock_exists):
        cg_explorer = CallGraphExplorer(self.repo)
        callees = cg_explorer.get_callees_from_identifier("src.classes.MyClass")
        self.assertEqual(len(callees), 3)
        expected_callees = [
            "<builtin>.print",
            "src.utils.baz",
            "src.classes.MyClass.my_method",
        ]
        for callee in callees:
            self.assertIsInstance(callee, (Method, Function))
            if isinstance(callee, Method):
                self.assertIn(callee.method_id.identifier, expected_callees)
            elif isinstance(callee, Function):
                self.assertIn(callee.function_id.identifier, expected_callees)


if __name__ == "__main__":
    unittest.main()
