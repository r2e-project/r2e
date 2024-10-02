"""Helper functions to run commmands and print stuff for the R2E guide."""

import os
import subprocess
import sys
import json

from IPython.display import clear_output
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown
from rich.table import Table
from rich.layout import Layout

from r2e.utils.data import load_functions
from r2e.paths import EXTRACTED_DATA_DIR


console = Console()


def run_command(command):
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True,
        text=True,
        bufsize=1,
    )

    output = []

    for line in iter(process.stdout.readline, ""):
        print(line, end="")  # This will display the line immediately
        sys.stdout.flush()  # Ensure it's displayed right away
        output.append(line)

    process.stdout.close()
    return_code = process.wait()

    if return_code != 0:
        raise Exception(f"Command failed with return code {return_code}")

    clear_output(wait=True)

    return "\n".join(output)


def color_test_names(names, color):
    return [Text(name.strip(), style=color) for name in names if name.strip()]


def summarize(step_id: int, step_name: str, exp_id: str, execution_output=None):
    console.print(Panel(Text(f"Step {step_id}: {step_name}", style="bold green")))

    if step_id == 3:
        # load the extracted functions
        data = load_functions(EXTRACTED_DATA_DIR / f"{exp_id}_extracted.json")
        functions = [f for f in data if hasattr(f, "function_id")]
        methods = [f for f in data if hasattr(f, "method_id")]
        classes = set(
            [f.parent_class_id for f in data if hasattr(f, "parent_class_id")]
        )

        # summarize # functions and methods in a markdown table using rich
        table = "| Functions | Methods | Classes | Repos |\n|-----------|---------|---------|-------|"
        table += f"\n| {len(functions)} | {len(methods)} | {len(classes)} | {1} |"
        console.print(Markdown(table))

    if step_id == 6:
        if execution_output:
            try:
                logs = json.loads(execution_output["logs"])
                test_results = logs["run_tests_logs"]["test_0"]
                coverage = logs["coverage_logs"][0]

                # Color-code test names
                passed_names = color_test_names(test_results["passed_names"], "green")
                failed_names = color_test_names(test_results["failed_names"], "red")
                errored_names = color_test_names(
                    test_results.get("errored_names", []), "yellow"
                )

                # Test Results Summary
                test_table = Table(title="Test Results Summary")
                test_table.add_column("Metric", style="cyan")
                test_table.add_column("Value", justify="right", style="magenta")
                test_table.add_column("Test Names", style="white")

                total_tests = (
                    test_results["passed_count"]
                    + test_results["failed_count"]
                    + test_results["errored_count"]
                )
                all_names = passed_names + failed_names + errored_names
                test_table.add_row("Total Tests", str(total_tests), "")
                test_table.add_row(
                    "Passed",
                    str(test_results["passed_count"]),
                    Text("\n").join(passed_names),
                )
                test_table.add_row(
                    "Failed",
                    str(test_results["failed_count"]),
                    Text("\n").join(failed_names),
                )
                test_table.add_row(
                    "Errored",
                    str(test_results["errored_count"]),
                    Text("\n").join(errored_names),
                )

                # Coverage Summary

                if coverage:
                    coverage_table = Table(title="Coverage Summary")
                    coverage_table.add_column("Metric", style="cyan")
                    coverage_table.add_column("Value", justify="right", style="magenta")
                    coverage_table.add_row(
                        "Line Coverage", f"{coverage['line_coverage_percentage']:.2f}%"
                    )
                    coverage_table.add_row(
                        "Branch Coverage",
                        f"{coverage['branch_coverage_percentage']:.2f}%",
                    )
                    coverage_table.add_row(
                        "Executable Lines", str(coverage["num_executable_lines"])
                    )
                    coverage_table.add_row(
                        "Executed Branches", str(coverage["num_executed_branches"])
                    )

                    # Create a layout for side-by-side display
                    layout = Layout()
                    layout.split_row(
                        Layout(test_table, ratio=3), Layout(coverage_table, ratio=2)
                    )
                    console.print(layout)
                else:
                    console.print(test_table)

            except (json.JSONDecodeError, KeyError) as e:
                console.print(
                    f"Error parsing execution output: {str(e)}", style="bold red"
                )
        else:
            console.print("No execution output provided for summary.", style="yellow")
