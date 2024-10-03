import fire
from tqdm import tqdm

from r2e.models import Tests
from r2e.generators.testgen import TestGenArgs, TestGenTask
from r2e.generators.testgen.utils import get_generated_tests
from r2e.llms.completions import LLMCompletions
from r2e.utils.data import load_functions_under_test, write_functions_under_test
from r2e.paths import TESTGEN_DIR, timestamp


class R2ETestOversample:

    @staticmethod
    def oversample(args):
        """Oversample the generated tests"""
        futs = load_functions_under_test(TESTGEN_DIR / args.in_file)

        # take the first test as the reference for oversampling
        ref_tests = [fut.tests["test_0"] for fut in futs]
        tasks = R2ETestOversample.prepare_tasks(futs)
        tasks = R2ETestOversample.update_tasks(tasks, ref_tests)

        for i in range(1, args.oversample_rounds + 1):
            payloads = [task.chat_messages for task in tasks]
            outputs = LLMCompletions.get_llm_completions(args, payloads)
            results = get_generated_tests(outputs)

            for fut, test in zip(futs, results):
                tests = Tests(
                    tests=fut.tests,
                    operation="oversample",
                    gen_model=args.model_name,
                    gen_date=timestamp(),
                )
                tests.add(f"test_{i}", test)
                fut.update_history(tests)

            tasks = R2ETestOversample.update_tasks(tasks, results)

        write_functions_under_test(futs, TESTGEN_DIR / f"{args.exp_id}_oversample.json")

    # task modifiers

    @staticmethod
    def prepare_tasks(functions) -> list[TestGenTask]:
        tasks = []

        for func in tqdm(functions):
            tasks.append(TestGenTask(func_meth=func))

        return tasks

    @staticmethod
    def update_tasks(tasks, results) -> list[TestGenTask]:
        for task, result in zip(tasks, results):
            task.update(result)

        return tasks


if __name__ == "__main__":
    args = fire.Fire(TestGenArgs)

    R2ETestOversample.oversample(args)
