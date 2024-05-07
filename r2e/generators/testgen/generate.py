import ast
import argparse
import tiktoken
import fire
from tqdm import tqdm

from r2e.models import Function, Method, Context, Tests
from r2e.models.fut import create_code_under_test

from r2e.pat.ast.transformer import RemoveMethodsTransformer
from r2e.generators.context import get_context_wrapper
from r2e.generators.testgen import TestGenTask, TestGenArgs
from r2e.llms.completions import LLMCompletions
from r2e.generators.testgen.utils import get_generated_tests
from r2e.multiprocess import run_tasks_in_parallel_iter
from r2e.utils.data import (
    load_functions,
    load_functions_under_test,
    write_functions,
    write_functions_under_test,
)
from r2e.paths import EXTRACTED_DATA_DIR, TESTGEN_DIR, timestamp


class R2ETestGenerator:

    @staticmethod
    def generate(args):
        """Generate tests for functions"""
        functions = load_functions(EXTRACTED_DATA_DIR / args.in_file)

        tasks = R2ETestGenerator.prepare_tasks(functions)
        payloads = [task.chat_messages for task in tasks]

        outputs = LLMCompletions.get_llm_completions(args, payloads)

        results = get_generated_tests(outputs)
        futs = [create_code_under_test(func) for func in functions]

        for fut, test in zip(futs, results):
            fut.update_history(
                Tests(
                    tests={"test_0": test},
                    gen_model=args.model_name,
                    gen_date=timestamp(),
                )
            )

        write_functions_under_test(futs, TESTGEN_DIR / f"{args.exp_id}_generate.json")

    @staticmethod
    def execute(args):
        """Execute the generated tests"""
        futs = load_functions_under_test(TESTGEN_DIR / args.in_file)

        # TODO: use docker client to execute tests
        # TODO: dump the results to disk
        # NOTE: (@manish): stats = {sample_id -> stats}; use fut.update_stats

        raise NotImplementedError("Connect to docker client to execute tests")

    @staticmethod
    def filter(args):
        """Filter failing tests from the generated tests"""
        futs = load_functions_under_test(TESTGEN_DIR / args.in_file)

        for fut in tqdm(futs):
            assert fut.exec_stats is not None
            filtered_tests = {}

            for sample_id, stats in fut.exec_stats.items():
                failed_tests = stats.get("failed_names", [])
                errored_tests = stats.get("errored_names", [])

                tests_to_filter = failed_tests + errored_tests
                test = fut.tests.get(sample_id, None)
                assert test is not None

                if tests_to_filter == []:
                    filtered_tests[sample_id] = test
                    continue

                transformer = RemoveMethodsTransformer(ast.parse(test), tests_to_filter)
                cleaned_test = ast.unparse(transformer.transform())
                filtered_tests[sample_id] = cleaned_test

            fut.update_history(
                Tests(tests=filtered_tests, operation="filter", gen_date=timestamp())
            )

        write_functions_under_test(futs, TESTGEN_DIR / f"{args.exp_id}_filter.json")

    @staticmethod
    def prepare_tasks(functions) -> list[TestGenTask]:
        context_gen_tasks = [(args.context_type, func, 6000) for func in functions]
        context_iter = run_tasks_in_parallel_iter(
            get_context_wrapper,
            context_gen_tasks,
            num_workers=8,
            use_progress_bar=True,
            progress_bar_desc="Generating contexts",
        )

        tasks = []

        for func, task_result in zip(functions, context_iter):
            if task_result.is_success():
                context = task_result.result
                func.add_context(context)
                tasks.append(TestGenTask(func_meth=func))
            else:
                print(f"Error generating context:\n{task_result.exception_tb}")

        return tasks

    @staticmethod
    def update_tasks(tasks, results) -> list[TestGenTask]:
        for task, result in zip(tasks, results):
            task.update(result)

        return tasks


if __name__ == "__main__":
    args = fire.Fire(TestGenArgs)

    R2ETestGenerator.generate(args)
