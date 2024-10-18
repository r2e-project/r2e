import fire
import re
import numpy as np
from collections import Counter

from r2e.utils.data import *
from r2e.paths import *


class TestGenEvaluator:
    """Evaluator that summarizes the results of
    test generation and execution."""

    def __init__(self, file_path):
        self.file_path = file_path
        self.results = load_functions_under_test(file_path)
        self.overall_metrics = {
            "total": len(self.results),
            "runnable": 0,
            "errored": 0,
            "valid": 0,
            "validity": 0.0,
            "coverage": 0.0,
        }

        self.repo_properties = {
            "repos": set(),
            "runnable_repos": set(),
            "valid_repos": set(),
        }

        self.problem_metrics = {
            "runnable_problems": set(),
            "valid_problems": set(),
        }

        self.code_properties = {
            "valid_lengths": [],
            "valid_executed_lengths": [],
            "valid_executed_branches": [],
        }

        self.coverage_metrics = {
            "valid_line_cov": [],
            "valid_branch_cov": [],
        }

        self.test_metrics = {
            "all_failed": 0,
            "all_errored": 0,
            "pass_ratios": [],
        }

        self.error_metrics = {"error_types": Counter()}

    def evaluate(self):
        for fut in self.results:
            self.evaluate_fut(fut)

        self.overall_metrics["runnable"] = len(
            self.problem_metrics["runnable_problems"]
        )
        self.overall_metrics["valid"] = len(self.problem_metrics["valid_problems"])
        self.overall_metrics["errored"] = (
            self.overall_metrics["total"] - self.overall_metrics["runnable"]
        )

        self.overall_metrics["validity"] = (
            self.overall_metrics["valid"] / self.overall_metrics["runnable"]
        ) * 100  # TODO: use total?

        self.overall_metrics["coverage"] = np.array(
            self.coverage_metrics["valid_branch_cov"]
        ).mean()

    def evaluate_fut(self, fut):
        self.repo_properties["repos"].add(fut.repo.repo_id)

        test_history = fut.test_history
        exec_stats = test_history.latest_exec_stats

        if exec_stats is None:
            raise ValueError("No execution stats found")

        elif "run_tests_logs" not in exec_stats:
            self.evaluate_errored_fut(fut, exec_stats)

        else:
            self.parse_exec_stats(fut, exec_stats)

    def evaluate_errored_fut(self, fut, exec_stats):
        output = exec_stats.get("output", "")  # TODO: useful here?
        error = exec_stats.get("error", "")

        for err in self.parse_stderr(error):
            self.error_metrics["error_types"][err["error_type"]] += 1

    # helper methods

    def parse_exec_stats(self, fut, exec_stats):
        self.repo_properties["runnable_repos"].add(fut.repo.repo_id)
        self.problem_metrics["runnable_problems"].add(fut.id)

        run_test_logs = exec_stats["run_tests_logs"]
        coverage_logs = exec_stats["coverage_logs"]
        is_valid = self.parse_run_test_logs(run_test_logs)

        if is_valid:
            self.repo_properties["valid_repos"].add(fut.repo.repo_id)
            self.problem_metrics["valid_problems"].add(fut.id)

            executed_lines, executed_branches, line_cov, branch_cov = (
                self.parse_coverage_logs(coverage_logs)
            )
            self.code_properties["valid_executed_lengths"].append(executed_lines)
            self.code_properties["valid_executed_branches"].append(executed_branches)
            self.coverage_metrics["valid_line_cov"].append(line_cov)
            self.coverage_metrics["valid_branch_cov"].append(branch_cov)

    def parse_run_test_logs(self, run_test_logs):
        is_valid = all(logs["valid"] for logs in run_test_logs.values())
        pass_c, fail_c, error_c = 0, 0, 0

        for _, logs in run_test_logs.items():
            pass_c += logs["passed_count"]
            fail_c += logs["failed_count"]
            error_c += logs["errored_count"]

        total_c = pass_c + fail_c + error_c
        pass_ratio = pass_c / total_c if total_c > 0 else 0
        self.test_metrics["pass_ratios"].append(pass_ratio)

        if pass_c + error_c == 0:
            self.test_metrics["all_failed"] += 1
        if pass_c + fail_c == 0:
            self.test_metrics["all_errored"] += 1

        return is_valid

    def parse_coverage_logs(self, coverage_logs):
        assert len(coverage_logs) == 1, "more than one func was tested?"
        coverage_logs = coverage_logs[0]

        executable_lines = coverage_logs["num_executable_lines"]
        excluded_lines = coverage_logs["num_excluded_lines"]
        unexecuted_lines = coverage_logs["num_unexecuted_lines"]

        executed_lines = executable_lines - excluded_lines - unexecuted_lines
        executed_branches = coverage_logs["num_executed_branches"]
        line_cov = coverage_logs["line_coverage_percentage"]
        branch_cov = coverage_logs["branch_coverage_percentage"]

        return executed_lines, executed_branches, line_cov, branch_cov

    def parse_stderr(self, stderr):
        lines = stderr.split("\n")
        error_lines = [l for l in lines if "Error:" in l or "Exception:" in l]
        error_messages = []

        error_regex = re.compile(
            r"(?P<error_type>\w+Error|Exception): (?P<error_message>.+)"
        )

        for l in error_lines:
            match = error_regex.match(l)
            if match:
                error_messages.append(
                    {
                        "error_type": match.group("error_type").strip(),
                        "error_message": match.group("error_message").strip(),
                    }
                )

        return error_messages

    def summarize_stat_data(self, data, label):
        data_array = np.array(data)
        mean = data_array.mean()
        std = data_array.std()

        print(f"{label} mean: {mean:.2f} | std: {std:.2f}")

        if data_array.dtype == np.float64:
            print(f" - {label} > 80%: {(data_array > 80).sum()}")
            print(f" - {label} > 90%: {(data_array > 90).sum()}")
            print(f" - {label} == 100%: {(data_array == 100).sum()}")
        else:
            print(f" - {label} == 1: {(data_array == 1).sum()}")
            print(f" - {label} == 2: {(data_array == 2).sum()}")
            print(f" - {label} > 5: {(data_array > 5).sum()}")
            print(f" - {label} > 10: {(data_array > 10).sum()}")


def summarize(exp_id):
    file_path = EXECUTION_DIR / f"{exp_id}_out.json"
    evaluator = TestGenEvaluator(file_path)
    evaluator.evaluate()

    print("=" * 20, "SUMMARY STATS", "=" * 20)
    print("Total problems:", evaluator.overall_metrics["total"])
    print("Runnable problems:", evaluator.overall_metrics["runnable"])
    print("Valid problems:", evaluator.overall_metrics["valid"])
    print("Errored problems:", evaluator.overall_metrics["errored"])
    print(f"Validity(%): {evaluator.overall_metrics['validity']:.2f}")
    print(f"Coverage(%): {evaluator.overall_metrics['coverage']:.2f}")

    print("=" * 20, "REPO STATS", "=" * 20)
    print("Total repos:", len(evaluator.repo_properties["repos"]))
    print("Runnable repos:", len(evaluator.repo_properties["runnable_repos"]))
    print("Valid repos:", len(evaluator.repo_properties["valid_repos"]))

    print("=" * 20, "COVERAGE STATS", "=" * 20)
    series_data = {
        "Valid Line coverage": evaluator.coverage_metrics["valid_line_cov"],
        "Valid Branch coverage": evaluator.coverage_metrics["valid_branch_cov"],
        "Valid Executed lengths": evaluator.code_properties["valid_executed_lengths"],
        "valid_executed_branches": evaluator.code_properties["valid_executed_branches"],
    }
    for label, series in series_data.items():
        evaluator.summarize_stat_data(series, label)

    print("=" * 20, "TEST STATUS STATS", "=" * 20)
    print("All failed:", evaluator.test_metrics["all_failed"])
    print("All errored:", evaluator.test_metrics["all_errored"])
    print(
        "Pass ratios mean: {:.2f} | std: {:.2f}".format(
            np.mean(evaluator.test_metrics["pass_ratios"]),
            np.std(evaluator.test_metrics["pass_ratios"]),
        )
    )

    print("=" * 20, "ERROR STATS", "=" * 20)
    print("Total error types:", len(evaluator.error_metrics["error_types"]))
    print("Error types:", dict(evaluator.error_metrics["error_types"]))


if __name__ == "__main__":
    fire.Fire(summarize)
