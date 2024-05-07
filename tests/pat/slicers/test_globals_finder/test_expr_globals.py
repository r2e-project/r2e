import ast
import unittest

from r2e.pat.dependency_slicer.globals_finder.expr_globals import get_expr_globals


class TestExprGlobalsFinder(unittest.TestCase):
    def build_ast_get_exp_globals(self, code: str):
        node = ast.parse(code).body[0]
        return get_expr_globals(node)  # type: ignore

    def compare(self, code, expected):
        predicted = self.build_ast_get_exp_globals(code)
        self.assertEqual(set(predicted), set(expected))

    def test_constant(self):
        self.compare("1", [])

    def test_name(self):
        self.compare("y", ["y"])

    def test_attribute(self):
        self.compare("y.z", ["y"])

    def test_call(self):
        self.compare("y(a,1)", ["y", "a"])

    def test_list(self):
        self.compare("[1,a]", ["a"])
        self.compare("(1,(a, [1, {b, x}]))", ["a", "b", "x"])

    def test_tuple(self):
        self.compare("(1, a, b)", ["a", "b"])

    def test_set(self):
        self.compare("{1, a, b}", ["a", "b"])

    def test_dict(self):
        self.compare("{1:a,b:2}", ["a", "b"])
        self.compare("{1:a,b:2,c:d}", ["a", "b", "c", "d"])

    def test_subscript(self):
        self.compare("y[1]", ["y"])
        self.compare("y[a:b]", ["y", "a", "b"])
        self.compare("y[a:b:x[c]]", ["y", "a", "b", "x", "c"])

    def test_binop(self):
        self.compare("a+b", ["a", "b"])
        self.compare("a+b*c", ["a", "b", "c"])

    def test_unaryop(self):
        self.compare("-a", ["a"])

    def test_slice(self):
        self.compare("a[b:c]", ["a", "b", "c"])
        self.compare("a[b:c:d]", ["a", "b", "c", "d"])

    def test_lambda(self):
        self.compare("lambda x: x", [])
        self.compare("lambda x: x+y", ["y"])
        self.compare("lambda x: x+1+z", ["z"])

    def test_ifexp(self):
        self.compare("a if b else c", ["a", "b", "c"])
        self.compare(
            "a if b else c if d else e if f else g", ["a", "b", "c", "d", "e", "f", "g"]
        )

    def test_dictcomp(self):
        self.compare("{a:b for a,b in c}", ["c"])
        self.compare("{a:b for a,b in c if a+d >= 0}", ["c", "d"])

    def test_setcomp(self):
        self.compare("{a for a in b}", ["b"])
        self.compare("{a for a in b if a > 0}", ["b"])

    def test_generator(self):
        self.compare("(a for a in b)", ["b"])
        self.compare("(a for a in b if a > 0)", ["b"])

    def test_listcomp(self):
        self.compare("[a for a in b]", ["b"])
        self.compare("[x+a for a in b for b in c if len(b)+y]", ["c", "x", "y", "len"])

    def test_await(self):
        self.compare("await a", ["a"])

    def test_yield(self):
        self.compare("yield a", ["a"])

    def test_yield_from(self):
        self.compare("yield from a", ["a"])

    def test_compare(self):
        self.compare("a == b == c == d", ["a", "b", "c", "d"])

    def test_boolop(self):
        self.compare("a and b and c or d", ["a", "b", "c", "d"])

    def test_joinedstr(self):
        self.compare("f'{a} {b}'", ["a", "b"])
        self.compare("f'{a} {b} {c}'", ["a", "b", "c"])
        self.compare("f'{a} {b} {c} {d}'", ["a", "b", "c", "d"])

    def test_formattedvalue(self):
        self.compare("f'{a}'", ["a"])
        self.compare("f'{a+b}'", ["a", "b"])
        self.compare("f'{a+b+c}'", ["a", "b", "c"])

    def test_starred(self):
        self.compare("*a", ["a"])
        self.compare("*a, b", ["a", "b"])
        self.compare("*a, b, c", ["a", "b", "c"])

    def test_namedexpr(self):
        self.compare("(a := b)", ["b"])


if __name__ == "__main__":
    unittest.main()
