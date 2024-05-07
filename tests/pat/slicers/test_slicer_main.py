import os
import ast
import sys
import unittest

from r2e.multiprocess import run_tasks_in_parallel_iter
from r2e.utils.data import load_functions
from r2e.pat.dependency_slicer import DependencySlicer
from r2e.models import Repo, Function, Method
from r2e.logger import logger
from r2e.paths import REPOS_DIR, EXTRACTION_DIR


ALL_FUNCTIONS = load_functions(EXTRACTION_DIR / "r2e_v1_extracted.json")


def get_slice(func_idx: int):
    func = ALL_FUNCTIONS[func_idx]
    if not os.path.exists(REPOS_DIR / func.repo.local_repo_path.split("/")[-1]):
        logger.warning(
            f"Skipping {func.id} - no local repo path {func.repo.local_repo_path}"
        )
        return
    if isinstance(func, Function):
        slicer = DependencySlicer.from_function_models(func)
        slicer.run()
    elif isinstance(func, Method):
        slicer = DependencySlicer.from_class_models(func.parent_class)
        slicer.run()
    else:
        raise ValueError(f"Unknown function type: {type(func)}")

    # print(slicer.dependency_graph.unparse())
    return slicer.dependency_graph.unparse()


# @unittest.skip("Skip for clean stdout")
class TestSlicerMain(unittest.TestCase):

    # def test_slicer_single(self):
    #     res = run_tasks_in_parallel_iter(
    #         get_slice, list(range(len(ALL_FUNCTIONS))), 32, use_progress_bar=True
    #     )
    #     for idx, r in enumerate(res):
    #         if r.is_success():
    #             sliced_program = r.result
    #             sliced_program_ast = ast.parse(sliced_program)
    #             new_program = ""
    #             # for stmt in sliced_program_ast.body:
    #             #     if isinstance(stmt, (ast.Import, ast.ImportFrom)):
    #             #         stmt_lines = ast.unparse(stmt).split("\n")
    #             #         for line in stmt_lines:
    #             #             new_program += f"{line}  # type: ignore\n"
    #             #     elif isinstance(stmt, ast.FunctionDef):
    #             #         ## add type ignore to function definition via ast
    #             #         ## definition might be split into multiple lines and have decorator(s)
    #             #         stmt_lines = ast.unparse(stmt).split("\n")
    #             #         seen_func_end = False
    #             #         for line in stmt_lines:
    #             #             if seen_func_end:
    #             #                 new_program += f"{line}\n"
    #             #             else:
    #             #                 new_program += f"{line}  # type: ignore\n"
    #             #                 if line.endswith(":"):
    #             #                     seen_func_end = True

    #             #     else:
    #             #         new_program += ast.unparse(stmt) + "\n"

    #             new_program = sliced_program
    #             with open(f"/tmp/slices/{idx}.py", "w") as fp:
    #                 fp.write(new_program)
    #         else:
    #             print(r.exception_tb, file=sys.stderr)

    def test_slicer_specific(self):
        functions = [
            f for f in ALL_FUNCTIONS if f.id == "klongpy.monads.eval_monad_range"
        ][0]
        assert isinstance(functions, Function)

        slicer = DependencySlicer.from_function_models(functions)
        slicer.run()
        # print(slicer.dependency_graph.unparse())

    def test_slicer_specific2(self):
        functions = [
            f for f in ALL_FUNCTIONS if f.id == "sacpy.XrTools.spec_moth_yrmean"
        ][0]
        assert isinstance(functions, Function)

        slicer = DependencySlicer.from_function_models(functions)
        slicer.run()
        # print(slicer.dependency_graph.unparse())

    def test_slicer_multiple(self):
        functions = [
            f
            for f in ALL_FUNCTIONS
            if isinstance(f, Function)
            if f.file.file_module.module_id.identifier == "chainfury.base"
        ]

        slicer = DependencySlicer.from_function_models(functions)
        slicer.run()
        # print(slicer.dependency_graph.unparse())

    def test_slicer_multiple_from_file(self):
        file = REPOS_DIR / "klongpy/klongpy/monads.py"
        with open(file, "r") as f:
            tree = ast.parse(f.read())
        functions = [f for f in tree.body if isinstance(f, ast.FunctionDef)]
        file_obj_dict = {
            "file_module": {
                "module_id": {"identifier": "klongpy.monads"},
                "module_type": "file",
                "repo": {
                    "repo_org": "",
                    "repo_name": "klongpy",
                    "repo_id": "klongpy",
                    "local_repo_path": "repos/klongpy",
                },
            }
        }
        function_dicts = []
        for function in functions:
            function_dicts.append(
                {
                    "function_id": {"identifier": function.name},
                    "function_name": function.name,
                    "function_complexity": "blah",
                    "function_code": ast.unparse(function),
                    "file": file_obj_dict,
                    "sliced_context": None,
                    "full_context": None,
                }
            )
        functions = [Function(**f) for f in function_dicts]

        slicer = DependencySlicer.from_function_models(functions)
        slicer.run()
        # print(slicer.dependency_graph.unparse())

    def test_slicer_multiple2(self):
        file = str(REPOS_DIR / "autoagents/autoagents/eval/hotpotqa/eval_async.py")

        repo = Repo(
            repo_org="",
            repo_name="autoagents",
            repo_id="autoagents",
            local_repo_path=f"repos/autoagents",
        )

        with open(file, "r") as f:
            tree = ast.parse(f.read())
        function_names = [f.name for f in tree.body if isinstance(f, ast.FunctionDef)]
        function_objs = []
        for function_name in function_names:
            function_objs.append(
                Function.from_name_file_repo(function_name, file, repo)
            )

        slicer = DependencySlicer.from_function_models(function_objs)
        slicer.run()
        # print(slicer.dependency_graph.unparse())

    def test_slicer_multiple3(self):
        file = str(REPOS_DIR / "stable-ts/stable_whisper/audio.py")

        repo = Repo(
            repo_org="",
            repo_name="stable-ts",
            repo_id="stable-ts",
            local_repo_path=f"repos/stable-ts",
        )

        with open(file, "r") as f:
            tree = ast.parse(f.read())

        function_names = [f.name for f in tree.body if isinstance(f, ast.FunctionDef)]
        function_objs = []

        for function_name in function_names:
            function_objs.append(
                Function.from_name_file_repo(function_name, file, repo)
            )

        slicer = DependencySlicer.from_function_models(function_objs)
        slicer.run()

        # print(slicer.dependency_graph.unparse())

    def test_slicer_repo_1(self):
        repo_name = "social-network-link-prediction"
        repo_path = REPOS_DIR / repo_name

        repo = Repo(
            repo_org="",
            repo_name=repo_name,
            repo_id=repo_name,
            local_repo_path=f"repos/{repo_name}",
        )

        all_functions = []

        for root, dirs, files in os.walk(repo_path):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    with open(file_path, "r") as f:
                        tree = ast.parse(f.read())
                    function_names = [
                        f.name for f in tree.body if isinstance(f, ast.FunctionDef)
                    ]
                    function_objs = [
                        Function.from_name_file_repo(f, file_path, repo)
                        for f in function_names
                    ]
                    all_functions.extend(function_objs)

        slicer = DependencySlicer.from_function_models(all_functions)
        slicer.run()
        # print(slicer.dependency_graph.unparse())
