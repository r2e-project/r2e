import ast
import unittest

from r2e.pat.dependency_slicer.globals_finder.type_annotation_globals import (
    astnode_to_type_annotation_globals,
)


class TestTypeAnnGlobalsFinder(unittest.TestCase):
    def build_ast_get_type_annotation_globals(self, code: str):
        node = ast.parse(code).body[0]
        assert isinstance(node, (ast.FunctionDef, ast.ClassDef))
        return astnode_to_type_annotation_globals(node)

    def compare(self, code, expected):
        predicted = self.build_ast_get_type_annotation_globals(code)
        self.assertEqual(set(predicted), set(expected))

    def test_type_annotation_globals_name(self):
        code = "def foo(a: int, b: str): pass"
        self.compare((code), ["int", "str"])

    def test_type_annotation_globals_subscript(self):
        code = "def foo(a: List[int], b: dict[str, int]): pass"
        self.compare(
            code,
            ["List", "int", "dict", "str", "int"],
        )

    def test_type_annotation_globals_tuple(self):
        code = "def foo(a: Tuple[int, str], b: Tuple[str, int]): pass"
        self.compare(
            code,
            ["Tuple", "int", "str", "Tuple", "str", "int"],
        )

    def test_type_annotation_constant(self):
        code = "def foo(a: 'int', b: 'str'): pass"
        self.compare(code, ["int", "str"])
        code = "def foo(a: 1): pass"
        self.compare(code, [])

    def test_type_annotation_binop(self):
        code = "def foo(a: int | str, b: float | None): pass"
        self.compare(
            code,
            ["int", "str", "float", "None"],
        )

    def test_type_annotation_complex(self):
        code = "def foo(a: List[int | str], b: Tuple[tuple[list[float|None] | str], int]): pass"
        self.compare(
            code,
            [
                "List",
                "int",
                "str",
                "Tuple",
                "tuple",
                "list",
                "float",
                "None",
                "str",
                "int",
            ],
        )

    def test_type_annotation_list_str(self):
        code = "def foo(a:Literal['python', 'json']): pass"
        self.compare(
            code,
            ["Literal"],
        )


if __name__ == "__main__":
    unittest.main()
