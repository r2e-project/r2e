"""Utilities to read and write data from disk."""

import json
from pathlib import Path


from r2e.models.function import Function
from r2e.models.method import Method
from r2e.models.fut import FunctionUnderTest, MethodUnderTest
from r2e.models.codegen_problem import CodeGenProblemFunction, CodeGenProblemMethod


def load_json(file_path: str | Path) -> dict | list:
    """Load a JSON file from disk."""
    with open(file_path, "r") as f:
        return json.load(f)


def load_functions(file_path: str | Path) -> list[Function | Method]:
    """Load function and methods data from disk."""
    data = load_json(file_path)
    functions = []
    for func_data in data:
        if func_data.get("function_id"):
            functions.append(Function(**func_data))
        elif func_data.get("method_id"):
            functions.append(Method(**func_data))
        else:
            raise ValueError("Unknown input type")
    return functions


def load_functions_under_test(
    file_path: str | Path,
) -> list[FunctionUnderTest | MethodUnderTest]:
    """Load FUT data from disk."""
    data = load_json(file_path)
    functions = []
    for func_data in data:
        if func_data.get("function_id"):
            ## TODO temp due to bad code
            func_data["file"]["file_module"]["repo"]["repo_name"] = func_data["file"][
                "file_module"
            ]["repo"]["repo_id"]
            func_data["file"]["file_module"]["repo"]["repo_org"] = func_data["file"][
                "file_module"
            ]["repo"]["repo_id"]
            functions.append(FunctionUnderTest(**func_data))
        elif func_data.get("method_id"):
            func_data["file"]["file_module"]["repo"]["repo_name"] = func_data["file"][
                "file_module"
            ]["repo"]["repo_id"]
            func_data["file"]["file_module"]["repo"]["repo_org"] = func_data["file"][
                "file_module"
            ]["repo"]["repo_id"]
            functions.append(MethodUnderTest(**func_data))
        else:
            raise ValueError("Unknown input type")
    return functions


def write_functions(
    functions: list[Function | Method] | list[FunctionUnderTest], file_path: str | Path
) -> None:
    """Write function data to disk."""
    data = [func.model_dump() for func in functions]
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)


def write_functions_under_test(
    functions: list[FunctionUnderTest | MethodUnderTest], file_path: str | Path
) -> None:
    """Write FUT data to disk."""
    data = [func.model_dump() for func in functions]
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)


def write_codegen_problems(
    codegen_problems: list[CodeGenProblemFunction | CodeGenProblemMethod],
    file_path: str | Path,
) -> None:
    """Write codegen problems to disk."""
    data = [prob.model_dump() for prob in codegen_problems]
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)
