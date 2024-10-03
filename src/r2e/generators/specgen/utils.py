import random
import ast
from collections import defaultdict


def extract_code(output):
    """
    Extracts code from a given output string.

    Args:
        output (str): The output string to extract code from.

    Returns:
        str: The extracted code.
    """
    outputlines = output.split("\n")
    indexlines = [i for i, line in enumerate(outputlines) if "```" in line]
    if len(indexlines) < 2:
        return ""
    return "\n".join(outputlines[indexlines[-2] + 1 : indexlines[-1]])


def parse_new_docstring(output):
    """
    Parses a new docstring from a given output string.

    Args:
        output (str): The output string to parse the docstring from.

    Returns:
        str: The parsed docstring.
    """
    code = extract_code(output)
    if code == "":
        return ""
    try:
        tree = ast.parse(code).body[-1]
        docstring = ast.get_docstring(tree)  # type: ignore
        return docstring
    except SyntaxError:
        return ""


def get_new_specs(outputs):
    """
    Gets new specifications from a list of outputs.

    Args:
        outputs (list): The list of outputs to get the specifications from.

    Returns:
        list: The list of new specifications.
    """
    outputs = [output[0] for output in outputs]
    specs = [parse_new_docstring(output) for output in outputs]
    return specs


def build_captured_string(arg):
    """
    Builds a captured string from a given argument.

    Args:
        arg (dict): The argument to build the captured string from.

    Returns:
        str: The built captured string.
    """
    serialized_inputs = arg["serialized_inputs"]
    serialized_output = arg["serialized_output"]
    serialized_inputs = [f"{k}={v}" for k, v in serialized_inputs.items()]
    serialized_inputs = "\n".join(serialized_inputs)
    new_string = (
        f"Input Arguments:\n{serialized_inputs}\n\nOutput:\n{serialized_output}"
    )
    return new_string


def get_captured_types(args):
    """
    Gets captured types from a list of arguments.

    Args:
        args (list): The list of arguments to get the captured types from.

    Returns:
        tuple: The merged input types and output types.
    """
    input_types = [arg["input_types"] for arg in args]
    merged_input_types = defaultdict(list)
    for input_type in input_types:
        for k, v in input_type.items():
            merged_input_types[k].append(v)
    merged_input_types = "\n".join(
        [f"{k} : {', '.join(list(set(v)))}" for k, v in merged_input_types.items()]
    )

    output_types = [arg["output_type"] for arg in args]
    output_types = ", ".join(list(set(output_types)))
    return merged_input_types, output_types


def get_example_io_substring(captured_args):
    """
    Gets an example IO substring from a list of captured arguments.

    Args:
        captured_args (list): The list of captured arguments to get the example IO substring from.

    Returns:
        str: The example IO substring.
    """
    captured_args_strings = [build_captured_string(arg) for arg in captured_args]

    if len(captured_args_strings) > 0:
        example_io = random.sample(captured_args_strings, 1)[0]
        example_substring = f"Example IO:\n{example_io}\n\n"
    else:
        example_substring = ""

    return example_substring
