import ast
import unittest

from r2e.pat.dependency_slicer.globals_finder.stmt_globals import get_stmt_globals


class TestStmtGlobalsFinder(unittest.TestCase):
    def build_ast_getstmt_globals(self, code: str):
        node = ast.parse(code).body[0]
        return get_stmt_globals(node)  # type: ignore

    def compare(self, code, expected):
        predicted = self.build_ast_getstmt_globals(code)
        self.assertEqual(set(predicted), set(expected))

    def test_complex_function(self):
        code = """
def f(a : str, f_arg : int, arg2):
    import os
    global e
    a = 1
    b = a + b_f
    c = a + c_global()
    d = 4 + d_f(d_arg_global)
    e += 1 + f_arg
    return arg2 + arg1 +f()
    """
        self.compare(
            code,
            [
                "b_f",
                "c_global",
                "d_f",
                "d_arg_global",
                "e",
                "arg1",
                "str",
                "int",
            ],
        )

    def test_function(self):
        code = """
def f(a : str, f_arg : int, arg2):
    a = 1
    b = a + b_f
    c = a + c_global()
    """
        self.compare(code, ["b_f", "c_global", "str", "int"])

    def test_function_with_constructs(self):
        code = """
def f(a : str, f_arg : int, arg2):
    a = 1
    for i in range(b):
        i = x+1
        for_var = a+b+c
        while for_var < 10:
            for_var += delta
            if (random==1):
                random.randint(1,10)
            else:
                with open("file.txt") as f:
                    return delta + for_var + f.read()
        return delta + for_var
    
    try:
        assert alpha!=omega, f"{alpha=} is equal to {omega=}"
    except TypeError as e:
        print(e)
    except ValueError as e:
        print(e, alpha, beta)
    except Exception as e:
        print(e)

    def func2(a: Literal['gpt'], b: "Class" = GLOBAL_CLASS_INSTANCE):
        class A(B):
            RANDOM = RANDOM_GLOBAL**2
            def __init__(self, a, b):
                super().__init__(a)
                self.RANDOM_INTERNAL = RANDOM_GLOBAL + A.RANDOM + a + b
                A.works()

            @staticmethod
            def works(self):
                self.a + a + f_arg

            @property
            def x(self):
                print("getter of x called")
                return self._x

            @x.setter
            def x(self, value):
                print("setter of x called")
                self._x = value

            @x.deleter
            def x(self):
                print('deleter of x called')
                del self._x
        return a + b + new_var
    
    aaaa = xxxx = bbb + cccc + d(1,2,aaa,bbbbb) + ['xx']

    """
        self.compare(
            code,
            [
                "range",
                "b",
                "x",
                "c",
                "delta",
                "random",
                "open",
                "int",
                "str",
                "alpha",
                "omega",
                "TypeError",
                "print",
                "ValueError",
                "beta",
                "Exception",
                "Literal",
                "Class",
                "B",
                "RANDOM_GLOBAL",
                "staticmethod",
                "new_var",
                "super",
                "GLOBAL_CLASS_INSTANCE",
                "bbb",
                "cccc",
                "d",
                "aaa",
                "bbbbb",
                "property",
            ],
        )

    def test_class(self):
        code = """
class A(B):
    aa = 1
    bb = ax + b_f

    def __init__(self, a, b):
        super().__init__(a)
        self.a = a
        self.b = b
    
    def f(self):
        return self.a + self.b + z
    
    @staticmethod
    def f_static():
        return 1
    
    @classmethod
    def f_class(cls):
        return 1
    
    @property
    def f_property(self):
        return 1
    """
        self.compare(
            code,
            ["ax", "B", "b_f", "super", "property", "staticmethod", "classmethod", "z"],
        )

    def test_assign(self):
        self.compare("a = b+c + d(1,2,a,b)", ["b", "c", "d", "a"])
        # self.compare("a = x = b + c + d(1,2,a,b)", ["b", "c", "d", "a"])

    def test_augassign(self):
        self.compare("a += b+c + d(1,2,b)", ["b", "c", "d", "a"])
        self.compare("a += x +y", ["x", "y", "a"])

    def test_annassign(self):
        self.compare("a : int = 1", ["int"])
        self.compare("a : int = b + c", ["int", "b", "c"])
        self.compare("a : int", ["int"])

    def test_for(self):
        code = """
for i in range(1, 10, counter):
    for j in b:
        temp = a[j] if a[j] > a[i] else a[i]
        a[j] = temp
        a[i] = temp - a[j]
"""
        # self.compare(code, ["range", "counter", "b", "a"])
        self.compare(code, ["range", "counter", "b", "a"])

    def test_while(self):
        code = """
while i < 10:
    i = i-1
    j = j+1
"""
        self.compare(code, ["i", "j"])
