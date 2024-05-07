import ast
import unittest

from r2e.pat.dependency_slicer.globals_finder.defaultarg_globals import (
    get_defaultarg_globals,
)


class TestDefGlobalsFinder(unittest.TestCase):
    def build_ast_get_def_globals(self, code: str):
        node = ast.parse(code).body[0]
        assert isinstance(node, ast.FunctionDef)
        return get_defaultarg_globals(node)

    def compare(self, code, expected):
        predicted = self.build_ast_get_def_globals(code)
        self.assertEqual(set(predicted), set(expected))

    def test_def_globals_name_constants(self):
        code = "def foo(a=1, b=c): pass"
        self.compare(code, ["c"])

    def test_def_globals_attribute_function(self):
        code = "def foo(a=c.d, b=bar(x=y)): pass"
        self.compare(
            code,
            ["c", "bar"],
        )

    def test_def_globals_list_str(self):
        code = "def foo(a=['python', 'json']): pass"
        self.compare(
            code,
            [],
        )

    def test_def_globals_subscript(self):
        code = "def foo(a=b[0], c=d[x:y:z], e=f[abc]): pass"
        self.compare(code, ["b", "d", "x", "y", "z", "f", "abc"])

    def test_def_list_dict(self):
        code = "def foo(a=[1, 2], b={1: 2}, c=[bar(x=y), d], d={alpha:beta}): pass"
        self.compare(code, ["bar", "d", "alpha", "beta"])


if __name__ == "__main__":
    unittest.main()
