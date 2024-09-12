import ast
import json

from rich.text import Text
from rich.progress import Progress
from rich.panel import Panel
from rich.console import Console
import time

from r2e.models.method import Method
from r2e.utils.data import load_functions_under_test
from r2e.paths import TESTGEN_DIR

from utils import *

console = Console()
service = get_service()
FUNCTION_UNDER_TEST = "find_dependency_globals"

# LOAD the generated equivalence tests for the function
func_meths = load_functions_under_test(TESTGEN_DIR / "demo_generate.json")
func_meth = [fm for fm in func_meths if fm.name == FUNCTION_UNDER_TEST][0]
print_header(func_meth)

# SETUP the function, repo and tests w/ the r2e-test-server
# Prereq: $> r2e-test-server start
repo_data = get_repo_data(func_meth.repo)
function_data = get_function_data(func_meth)
tests = get_generated_tests(func_meth)

service.setup_repo(repo_data)
service.setup_function(function_data)
service.setup_test(tests)

out = service.init()
print(out)

####### Execute an example refactored function #######
with open("./demos/refactor/soln.txt", "r") as file:
    refactored_code = file.read()
    console.print()
    header = Text("Refactored Code", style="bold yellow")
    console.print(Panel(header, expand=False))
    console.print(refactored_code)
    console.print()

service.setup_codegen_mode()
out = service.execute(refactored_code)
print(out)

out = service.submit()

####### Print the output #######

console.print()
console.print(Panel(Text("Result", style="bold green"), expand=False))
print(out["error"])
print(out["output"])
temp = json.loads(out["logs"])
temp.pop("captured_arg_logs")
print(json.dumps(temp, indent=4))
