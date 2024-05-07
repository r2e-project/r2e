import ast
import unittest

from r2e.pat.dependency_slicer.globals_finder.bytecode_globals import (
    get_funclass_globals,
)


class TestBytecodeGlobalsFinder(unittest.TestCase):
    def build_ast_get_global_access_symbols(self, code: str):
        node = ast.parse(code).body[0]
        assert isinstance(
            node,
            (
                ast.FunctionDef,
                ast.ClassDef,
                ast.AsyncFunctionDef,
            ),
        )
        return get_funclass_globals(node)

    def compare(self, code, expected):
        predicted = self.build_ast_get_global_access_symbols(code)
        self.assertEqual(set(predicted), set(expected))

    def test_bytecode_globals(self):
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

    def test_bytecode_globals_async_og(self):
        code = """
async def collect_metrics(pred_dict: dict, dataset: dict, log_files: list):

    semaphore = asyncio.Semaphore(10)

    async def process_log_file(log_file: str):
        async with semaphore:
            with open(log_file, "r") as f:
                try:
                    log_data = json.load(f)
                except json.decoder.JSONDecodeError:
                    return
                await evaluate_log_data(log_data, pred_dict, dataset)

    await tqdm_asyncio.gather(*[
        process_log_file(log_file) for log_file in log_files
    ])
    """
        self.compare(
            code,
            ["open", "str", "asyncio", "json", "tqdm_asyncio", "evaluate_log_data"],
        )

    def test_bytecode_globals_nested(self):
        code = """
def f(a, b_f):
    global b_global
    d_f = lambda x: x
    def g():
        global e
        a = 1
        b = a + b_f
        c = a + c_global()
        d = 4 + d_f(d_arg_global)
        e += 1
        f += 2
        return a+b+c+d+e
    
    b_global += g()
    return
    """
        self.compare(
            code,
            ["c_global", "d_arg_global", "e", "b_global"],
        )

    def test_bytecode_globals_class(self):
        code = """
class A(B):
    a=1
    b=a+b_global
    c=a+c_global()

    def __init__(self, c: str = c_global()):
        self.d = 4 + d_global(d_arg)
        self.e += b + c + A.a + self.x
        return
    """
        ### TODO : this is incorrect
        ### self.compare(code, ["b_global", "c_global", "d_global", "d_arg"])
        self.compare(
            code,
            ["b_global", "c_global", "d_global", "d_arg", "a", "b", "str"],
        )

    def test_bytecode_globals_class_in_def(self):
        code = """def f():
    a = b

    class A(B):
        
        def __init__(self, a, b):
            super().__init__(a)
            self.a = a + temp
            self.b = b

        
        def x(self, value):
            print("setter of x called")
            self._x = value + temp

    return a + b + new_var"""
        self.compare(
            code,
            [
                "b",
                "temp",
                "new_var",
                "print",
                "super",
                "B",
            ],
        )

    def test_bytecode_globals_function_new(self):
        code = """
def f(x):
    a = b + x
    x += 1
    def g(d):
        return d + a + x
    return a + g(x) + new_var"""

        self.compare(
            code,
            ["b", "new_var"],
        )

    def test_bytecode_globals_setter(self):
        code = """class RequestStateTracker:

    def __init__(self, global_stats: VLLMEngineStatTracker):
        self._state: Optional[RequestState] = alpha
        self.global_stats = global_stats

    @x.setter
    def x(self, value):
        self._x = value + temp
"""
        ## NOTE : this is incorrect
        ## self.compare(code, ["VLLMEngineStatTracker", "alpha", "temp"])
        ## Optional and RequestState are added by type annotation for some reason :shrug:
        self.compare(
            code,
            ["VLLMEngineStatTracker", "x", "alpha", "temp"],
        )

    def test_bytecode_globals_fake_while(self):
        code = """def fake_func():
    while i < 10:
        i = i-1
        j = j+1
"""
        self.compare(
            code,
            ["i", "j"],
        )

    def test_bytecode_globals_fake_lambda(self):
        code = """def fake_func():
        d_f = lambda x: x
"""

        self.compare(
            code,
            [],
        )

    def test_bytecode_globals_async(self):
        code = """async def collect_metrics(pred_dict: dict, dataset: dict, log_files: list):

    semaphore = asyncio.Semaphore(10)

    async def process_log_file(log_file: str):
        async with semaphore:
            with open(log_file, "r") as f:
                try:
                    log_data = json.load(f)
                except json.decoder.JSONDecodeError:
                    return
                await evaluate_log_data(log_data, pred_dict, dataset)

    await tqdm_asyncio.gather(*[
        process_log_file(log_file) for log_file in log_files
    ])"""
        self.compare(
            code,
            ["open", "str", "asyncio", "json", "tqdm_asyncio", "evaluate_log_data"],
        )

    def test_bytecode_globals_fake_fors(self):
        code = """def fake():
    for b in c:
        for a in b:
            x+a
    """
        self.compare(
            code,
            ["x", "c"],
        )

    def test_bytecode_globals_fake_list_comprehension(self):
        code = """def fake():
    [x+a for a in b for b in c]
"""
        ## NOTE : a in b runs first so b is a global!
        self.compare(
            code,
            ["x", "b", "c"],
        )

    def test_bytecode_globals_fake_list_comprehension2(self):
        code = """def fake():
    [x+a for b in c for a in b]
"""
        self.compare(
            code,
            ["x", "c"],
        )

    def test_bytecode_globals_class_vars(self):
        code = """class A(B):
    a=1
    b=a+b_global
    c=a+c_global()

"""
        ## NOTE: this is incorrect
        ## self.compare(code, ["b_global", "c_global"])
        self.compare(
            code,
            ["a", "b_global", "c_global"],
        )

    def test_bytecode_globals_class_string_annoy(self):
        code = """class Router():
    @staticmethod
    def get_element_by_type(self, type: "BaseType"):
        return Elements[type]
"""
        ## NOTE: this is incorrect (BaseType as a string annotation)
        self.compare(
            code,
            ["staticmethod", "Elements"],
        )

    def test_bytecode_globals_class_string_annot2(self):
        code = """def fake():
    class Router():
        @staticmethod
        def get_element_by_type(self, type: "BaseType"):
            return Elements[type]
"""
        ## NOTE: this is incorrect (BaseType as a string annotation)
        self.compare(
            code,
            ["staticmethod", "Elements"],
        )
