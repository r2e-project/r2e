"""A simple agent-based test generator with execution and coverage feedback"""

import os
import fire
from tempfile import NamedTemporaryFile

from r2e.models import *
from r2e.utils.data import *
from r2e.paths import *

from r2e.execution.execute import EquivalenceTestRunner
from r2e.generators.testgen.args import GenExecArgs
from r2e.generators.testgen.generate import R2ETestGenerator
from r2e.generators.testgen.task import TestGenTask
from r2e.generators.testgen.utils import annotate_coverage


class R2EGenExec:

    @staticmethod
    def genexec(args):
        """Iteratively generate and execute tests for functions"""
        functions = load_functions(EXTRACTED_DATA_DIR / args.in_file)
        functions = functions[:10]

        if args.function:
            functions = [f for f in functions if f.name == args.function]

        final_output_file = EXECUTION_DIR / f"{args.exp_id}_out.json"
        worklist: list[TestGenTask] = R2ETestGenerator.prepare_tasks(args, functions)
        count = len(worklist)

        current_results: list[FunctionUnderTest | MethodUnderTest] = []
        futs = []

        for round in range(1, args.max_rounds + 1):
            print(f"Starting round {round}/{args.max_rounds}")
            # generate -> execute -> filter
            futs = R2EGenExec.generate(args, futs, worklist, round)
            futs = R2EGenExec.execute(args, futs)
            status_map, _continue = R2EGenExec.filter(futs, worklist, args)

            # update current results
            current_results = R2EGenExec._update_current_results(
                current_results, futs, status_map, round, args.max_rounds
            )

            # update worklist=tasks for failing futs
            worklist = R2EGenExec._update_worklist(worklist, futs, status_map, round)

            if not _continue or len(worklist) == 0:
                print(f"Reached minimum criteria. Stopping at round {round}")
                break

            if round == args.max_rounds:
                print(f"Reached max rounds. Stopping at round {round}")
                break

            good_ratio = (count - len(worklist)) / count
            print(f"Round {round} completed. Status: {good_ratio:.2f} good FUTs.\n")

        # sort the results in the order of the original functions
        sorted_results = R2EGenExec._sort_results(functions, current_results)
        write_functions_under_test(sorted_results, final_output_file)

    @staticmethod
    def generate(args, futs, worklist, round):
        """Generate tests for the worklist and return updated FUTs"""
        new_futs = R2ETestGenerator._generate(args, worklist, test_id=round - 1)
        if round == 1:
            futs = new_futs
        else:
            new_tests = {f.id: f.test_history.history[-1] for f in new_futs}
            futs = [f for f in futs if f.id in new_tests]
            for f in futs:
                f.update_history(new_tests[f.id])
        return futs

    @staticmethod
    def execute(args, futs):
        """Execute the tests for the functions and return updated FUTs"""
        with NamedTemporaryFile(mode="w", delete=False, suffix=".json") as tmp_file:
            write_functions_under_test(futs, tmp_file.name)
            args.in_file = tmp_file.name
            EquivalenceTestRunner.run(args)

        # load the executed futs and return
        futs = load_functions_under_test(EXECUTION_DIR / f"{args.exp_id}_out.json")
        return futs

    @staticmethod
    def filter(futs, tasks, args):
        good_futs, status_map = 0, {}

        for i, fut in enumerate(futs):
            fut_coverage = fut.coverage.get("branch_coverage_percentage", 0) / 100
            if fut.is_passing:
                if fut_coverage < args.min_cov:
                    status_map[i] = (False, "improve_coverage", annotate_coverage(fut))
                else:
                    good_futs += 1
                    status_map[i] = (True, None, None)
                continue

            # has no exec_stats --> a setup issue the LLM cannot fix
            if fut.exec_stats is None:
                continue

            # test run errored out or failed
            status_map[i] = (False, "fix_error", fut.errors)

        _continue = (good_futs / len(futs)) < args.min_valid
        return status_map, _continue

    ############################## helper functions ##############################

    @staticmethod
    def _update_worklist(worklist, futs, status_map, round):
        return [
            R2EGenExec._update_task(
                worklist[i], futs[i].tests[f"test_{round-1}"], ut, feedback
            )
            for i, (passing, ut, feedback) in status_map.items()
            if not passing
        ]

    @staticmethod
    def _update_task(task, result, update_type, feedback):
        task.update(result, feedback, update_type)
        return task

    @staticmethod
    def _update_current_results(current_results, futs, status_map, round, max_rounds):
        for i, (passing, _, _) in status_map.items():
            if passing:
                current_results.append(futs[i])
            elif round == max_rounds:
                current_results.append(futs[i])
        return current_results

    @staticmethod
    def _sort_results(functions, current_results):
        sorted_results = []
        for f in functions:
            for res in current_results:
                if res.id == f.id:
                    sorted_results.append(res)
                    break
        assert len(current_results) == len(functions)
        assert len(sorted_results) == len(functions)
        return sorted_results


if __name__ == "__main__":
    args = fire.Fire(GenExecArgs)
    R2EGenExec.genexec(args)
