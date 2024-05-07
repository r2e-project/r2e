import ast
import unittest

from r2e.pat.dependency_slicer.globals_finder import find_dependency_globals


class TestTypeAnnGlobalsFinder(unittest.TestCase):

    def build_ast_find_globals(self, code: str):
        node = ast.parse(code).body[0]
        return find_dependency_globals(node)

    def compare(self, code, expected):
        predicted = self.build_ast_find_globals(code)
        self.assertEqual(set(predicted), set(expected))

    def test_class_og(self):
        code = """
class RequestStateTracker:

    def __init__(self, global_stats: VLLMEngineStatTracker):
        self._state: Optional[RequestState] = None
        self.global_stats = global_stats

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state: RequestState):
        if state == self._state:
            return
        if self._state is not None:
            self.global_stats.exit_state(self._state)
        if state is not None:
            self.global_stats.enter_state(state)
        self._state = state

    def __del__(self):
        self.state = None"""

        # NOTE: setter stuff is being detected, can't heko
        # NOTE: bytecode detects type annotation in function arguments
        # but for some reason not in the body
        # expected = ["VLLMEngineStatTracker", "RequestState", "Optional"]
        expected = ["VLLMEngineStatTracker", "RequestState", "state", "Optional"]
        self.compare(code, expected)

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
            ["b_f", "c_global", "d_f", "d_arg_global", "e", "arg1"],
        )

    def test_function(self):
        code = """
def f(a : str, f_arg : int, arg2):
    a = 1
    b = a + b_f
    c = a + c_global()
    """
        self.compare(code, ["b_f", "c_global"])

    def test_string_type_ann(self):
        code = """
class ChildClass(ParentClass):
    def __init__(self, a: str):
        self.a = a
    
    def compare(self, b: "ParentClass"):
        return self.a == b

    """
        self.compare(code, ["ParentClass"])

    def test_string_type_ann2(self):
        code = """
class ChildClass(ParentClass):
    def __init__(self, a: str):
        self.a = a
    

    def typecast(self):
        b : "ParentClass" = ParentClass()
        return b

    """
        self.compare(code, ["ParentClass"])

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

    def func2(a: Literal['gpt'], b: Class = GLOBAL_CLASS_INSTANCE):
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
                "b",
                "x",
                "c",
                "delta",
                "random",
                "alpha",
                "omega",
                "beta",
                "Literal",
                "Class",
                "B",
                "RANDOM_GLOBAL",
                "new_var",
                "GLOBAL_CLASS_INSTANCE",
                "bbb",
                "cccc",
                "d",
                "aaa",
                "bbbbb",
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
            ["ax", "B", "b_f", "z"],
        )

    def test_assign(self):
        self.compare("a = b+c + d(1,2,x,b)", ["b", "c", "d", "x"])
        self.compare("a = x = b + c + d(1,2,y,b)", ["b", "c", "d", "y"])

    def test_augassign(self):
        self.compare("a += b+c + d(1,2,b)", ["b", "c", "d", "a"])
        self.compare("a += x +y", ["x", "y", "a"])

    def test_annassign(self):
        self.compare("a : int = 1", [])
        self.compare("a : int = b + c", ["b", "c"])
        self.compare("a : int", [])

    def test_for(self):
        code = """
for i in range(1, 10, counter):
    for j in b:
        temp : TempWrapper = a[j] if a[j] > a[i] else a[i]
        a[j] = temp
        a[i] = temp - a[j]
"""
        # self.compare(code, ["range", "counter", "b", "a"])
        self.compare(code, ["counter", "b", "a", "TempWrapper"])

    def test_while(self):
        code = """
while i < 10:
    i = i-1
    j = j+1
"""
        self.compare(code, ["i", "j"])

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
        self.compare("[x+a for b in c for a in b if len(b)+y]", ["c", "x", "y"])

    def test_await(self):
        self.compare("await a", ["a"])

    def test_yield(self):
        self.compare("yield a", ["a"])

    # def test_yield_from(self):
    #     self.compare("yield from a", ["a"])

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

    # def test_starred(self):
    #     self.compare("*a = b", ["b"])

    def test_namedexpr(self):
        self.compare("(a := b)", ["b"])
