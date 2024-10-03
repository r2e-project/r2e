import dis
import ast
import types
from collections import defaultdict

from r2e.pat.ast import build_ast


def compare_locations(instruction: dis.Instruction, node: ast.AST) -> bool:
    """
    Compare the location of the bytecode instruction and the ast node
    :param instruction: bytecode.Instr
    :param node: ast.AST
    :return: bool
    """
    return (
        instruction.positions is not None
        and instruction.positions.lineno == node.lineno  # type: ignore
        and instruction.positions.col_offset == node.col_offset  # type: ignore
        and instruction.positions.end_lineno == node.end_lineno  # type: ignore
        and instruction.positions.end_col_offset == node.end_col_offset  # type: ignore
    )


def build_id_to_nodes(module_ast: ast.Module) -> dict[str, list[ast.Name]]:
    id_to_nodes = defaultdict(list)
    for node in ast.walk(module_ast):
        if isinstance(node, ast.Name):
            id_to_nodes[node.id].append(node)
    return id_to_nodes


def get_argument_names(module_ast: ast.Module, code_obj: types.CodeType) -> list[str]:
    argument_names = []
    code_obj_name = code_obj.co_name
    code_obj_firstlineno = code_obj.co_firstlineno
    for node in ast.walk(module_ast):
        if (
            isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef)
        ) and node.name == code_obj_name:
            def_lineno_delta = [
                idx
                for idx, line in enumerate(ast.unparse(node).split("\n"))
                if line.strip().startswith("def")
                or line.strip().startswith("async def")
            ]
            assert len(def_lineno_delta) >= 1, ast.unparse(node)
            def_lineno_delta = def_lineno_delta[0]
            def_lineno = node.lineno - def_lineno_delta
            if def_lineno == code_obj_firstlineno:
                argument_names = (
                    [x.arg for x in node.args.args]
                    + [x.arg for x in node.args.kwonlyargs]
                    + [x.arg for x in [node.args.vararg, node.args.kwarg] if x]
                )
        if isinstance(node, ast.Lambda):
            argument_names = [x.arg for x in node.args.args]
    return argument_names


def handle_const_code(module_ast: ast.Module, code_obj: types.CodeType) -> list[str]:
    """
    Takes the module ast and the code object and returns the global variables accessed in the code object
    Particularly, it looks for LOAD_GLOBAL instructions which are loading the global variables.
    Similarly, it recursively looks for LOAD_CONST instructions which are loading the code objects
    :param module_ast: ast.Module
    :param code_obj: types.CodeType
    :return: list[str] - list of global variables accessed
    """
    argument_names = get_argument_names(module_ast, code_obj)

    fast_stores: list[str] = []

    code_bytecode = dis.Bytecode(code_obj)

    id_to_nodes: dict[str, list[ast.Name]] = build_id_to_nodes(module_ast)

    global_access_symbols = []
    for instruction in code_bytecode:
        if instruction.opname == "LOAD_GLOBAL":
            instruct_arg_name: str = instruction.argval  # type: ignore
            potential_nodes = id_to_nodes.get(instruct_arg_name, [])
            for potential_node in potential_nodes:
                if compare_locations(instruction, potential_node):
                    # print(f"Variable {instruct_arg_name} is load-global")
                    global_access_symbols.append(instruct_arg_name)

        elif instruction.opname == "STORE_FAST":
            instruct_arg_name: str = instruction.argval  # type: ignore
            fast_stores.append(instruct_arg_name)

        elif instruction.opname == "LOAD_FAST":
            instruct_arg_name: str = instruction.argval  # type: ignore
            potential_nodes = id_to_nodes.get(instruct_arg_name, [])
            for potential_node in potential_nodes:
                if compare_locations(instruction, potential_node):
                    if instruct_arg_name not in fast_stores:
                        ## means this is our fake function where
                        ## we have assignment of a variable before
                        ## initializing it
                        # print(f"Variable {instruct_arg_name} is used before assignment")
                        global_access_symbols.append(instruct_arg_name)

        elif instruction.opname == "LOAD_NAME":
            instruct_arg_name: str = instruction.argval  # type: ignore
            potential_nodes = id_to_nodes.get(instruct_arg_name, [])
            for potential_node in potential_nodes:
                if compare_locations(instruction, potential_node):
                    # print(f"Variable {instruct_arg_name} is load-name")
                    global_access_symbols.append(instruct_arg_name)

        elif instruction.opname == "LOAD_CONST":
            if isinstance(instruction.argval, types.CodeType):
                global_access_symbols.extend(
                    handle_const_code(module_ast, instruction.argval)
                )

        global_access_symbols = [
            g for g in global_access_symbols if g not in argument_names
        ]
    return global_access_symbols


def get_funclass_globals(
    func_class_ast: ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef,
) -> list[str]:
    """
    extract all the global variables accessed in the function
    uses the bytecode to extract the global variables
        - finds the LOAD_CONST instructions
        - finds the global variables in the constants using LOAD_GLOBAL
    :param func_class_ast: ast.FunctionDef
    :return: list[str] - list of global variables accessed
    """
    # we need ast.Module to compile and get this to work
    # so we will parse and unparse the function to get the module
    func_class_ast_str = ast.unparse(func_class_ast)
    module_ast = build_ast(func_class_ast_str, add_parents=False)
    module_ast = build_ast(ast.unparse(module_ast), add_parents=False)

    try:
        module_ast_compiled = compile(ast.unparse(module_ast), "<string>", "exec")
    except SyntaxError:
        print(f"Syntax error in {ast.unparse(module_ast)}")
        return []

    module_bytecode = dis.Bytecode(module_ast_compiled)

    global_access_symbols = []
    for instruction in module_bytecode:
        if instruction.opname == "LOAD_CONST":
            if isinstance(instruction.argval, types.CodeType):
                code = instruction.argval
                global_access_symbols.extend(handle_const_code(module_ast, code))

    function_name = func_class_ast.name
    global_access_symbols = [
        symbol for symbol in global_access_symbols if symbol != function_name
    ]
    return global_access_symbols
