import fire
from tqdm import tqdm

from r2e.generators.specgen.args import SpecGenArgs
from r2e.generators.specgen.task import SpecGenTask
from r2e.generators.specgen.utils import get_new_specs
from r2e.llms.completions import LLMCompletions
from r2e.utils.data import load_functions_under_test, write_codegen_problems
from r2e.models.codegen_problem import create_codegen_problem
from r2e.paths import R2E_BUCKET_DIR


class R2ESpecGenerator:

    @staticmethod
    def generate(args):
        """Generate specs for functions"""
        functions = load_functions_under_test(R2E_BUCKET_DIR / args.in_file)

        functions = functions[:5]

        tasks = R2ESpecGenerator.prepare_tasks(functions)
        payloads = [task.chat_messages for task in tasks]

        outputs = LLMCompletions.get_llm_completions(args, payloads)
        results = get_new_specs(outputs)

        codegen_probs = []
        for func, spec in zip(functions, results):
            codegen_probs.append(create_codegen_problem(func, spec))  # type: ignore

        write_codegen_problems(
            codegen_probs, R2E_BUCKET_DIR / f"{args.exp_id}_specgen.json"
        )

    @staticmethod
    def prepare_tasks(functions):
        """Prepare tasks for generating specs"""
        tasks = []

        for func in functions:
            generated_test = "\n".join(func.tests.values())
            tasks.append(SpecGenTask(func_meth=func, generated_test=generated_test))

        return tasks


if __name__ == "__main__":
    args = fire.Fire(SpecGenArgs)

    R2ESpecGenerator.generate(args)
