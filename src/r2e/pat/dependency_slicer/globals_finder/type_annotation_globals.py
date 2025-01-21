import ast

from r2e.pat.dependency_slicer.globals_finder.expr_globals import (
    ExprGlobalVariablesVisitor,
)


def collect_type_annotations(astnode: ast.AST) -> list[ast.AST]:
    """
    extract all the type annotations from a function or class
    :param astnode: ast.FunctionDef | ast.ClassDef
    :return: list[ast.AST] - list of type annotation AST nodes
    """
    type_annotations: list[ast.AST] = []

    for node in ast.walk(astnode):
        if isinstance(node, ast.AnnAssign):
            type_annotations.append(node.annotation)
        if isinstance(node, ast.arg):
            if node.annotation:
                type_annotations.append(node.annotation)
        if isinstance(node, ast.FunctionDef):
            if node.returns:
                type_annotations.append(node.returns)
        if isinstance(node, ast.ClassDef):
            if node.bases:
                type_annotations.extend(node.bases)
    return type_annotations


class TypeAnnotationGlobalVariablesVisitor(ExprGlobalVariablesVisitor):
    def visit_Constant(self, node) -> list[str]:
        if isinstance(node.value, str):
            try:
                node_parsed = ast.parse(node.value).body
            except SyntaxError:
                return []
            assert len(node_parsed) == 1 and isinstance(node_parsed[0], ast.Expr)
            node_parsed = node_parsed[0].value
            if isinstance(node_parsed, ast.Name):
                return [node.value]
            return []
        if node.value is None:
            return ["None"]
        if node.value == Ellipsis:
            return []
        # print(f"Weird constant: {node.value}")
        return []

    def visit_Subscript(self, node) -> list[str]:
        globals = self.visit(node.value)
        if ast.unparse(node.value) != "Literal":
            globals.extend(self.visit(node.slice))
        return globals


def type_annotations_to_globals(type_annotations: list[ast.AST]) -> list[str]:
    """
    parse all the global variables from the type annotations
    maps ast type and corresponding global variable appropriately
    :param type_annotations: list[ast.AST] - list of type annotation AST nodes
    :return: list[str] - list of global variables as strings
    """

    global_vars = []
    for type_ann in type_annotations:
        global_vars.extend(TypeAnnotationGlobalVariablesVisitor().visit(type_ann))
    return global_vars


def astnode_to_type_annotation_globals(
    astnode: ast.AST,
) -> list[str]:
    """
    extract all the global variables accessed in the type annotations of the function or class
    :param astnode: ast.FunctionDef | ast.ClassDef
    :return: list[str] - list of global variables accessed
    """
    type_annotations = collect_type_annotations(astnode)
    return type_annotations_to_globals(type_annotations)
