"""Utilities to interact with r2e-test-server: a server handles Python execution"""

import rpyc
import json

from rich.text import Text
from rich.console import Console
from rich.panel import Panel


console = Console()


def get_service():
    conn = rpyc.connect("localhost", 3006)
    service = conn.root
    return service


def get_repo_data(repo):
    return json.dumps(
        {
            "repo_id": None,
            "repo_path": repo.repo_path,
        }
    )


def get_function_data(func_meth):
    name, file_path = func_meth.execution_fut_data
    return json.dumps(
        {
            "funclass_names": [name],
            "file_path": file_path,
        }
    )


def get_generated_tests(fut):
    header = Text("Equivalence Test", style="bold magenta")
    console.print(Panel(header, expand=False))
    console.print(fut.tests["test_0"])
    return json.dumps({"generated_tests": fut.tests})


def print_header(func_meth):
    print("\n\n")
    print("=" * 234)
    print("\n\n")
    header = Text("Function", style="bold yellow")
    console.print(Panel(header, expand=False))
    console.print(func_meth.code)
    console.print()
