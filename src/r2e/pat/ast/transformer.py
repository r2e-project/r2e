import ast


class ASTTransformer(ast.NodeTransformer):
    """Base class for AST transformer."""

    def __init__(self, tree: ast.Module):
        self.tree = tree

    def transform(self):
        return super().visit(self.tree)


class ImportAliasReplacer(ASTTransformer):
    """Replace aliases of imports with original name in the code.

    Args:
        tree (ast.Module): AST tree of the code.
        names (list[str]): list of original names to be used in the code.
    """

    def __init__(self, tree: ast.Module, names: list[str]):
        super().__init__(tree)
        self.aliases = self.get_all_aliases(names)

    def get_all_aliases(self, names: list[str]) -> dict:
        aliases = {}
        for node in self.tree.body:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                for alias in node.names:

                    # if alias is used and it is not same as name
                    if alias.asname and alias.asname not in names:

                        # replace alias with name itself
                        if alias.name in names:
                            aliases[alias.asname] = alias.name

        return aliases

    def visit_Name(self, node):
        if node.id in self.aliases:
            return ast.copy_location(
                ast.Name(id=self.aliases[node.id], ctx=node.ctx), node
            )
        return node


class RemoveFunctionTransformer(ASTTransformer):
    """Remove a function from the code.

    Args:
        tree (ast.Module): AST tree of the code.
        function_name (str): the name of the function to remove
    """

    def __init__(self, tree: ast.Module, function_name: str):
        super().__init__(tree)
        self.function_name = function_name
        self.removed_node = None

    def visit_FunctionDef(self, node):
        if node.name == self.function_name:
            # save the removed code for later use
            self.removed_node = node
            return None
        return node


class RemoveClassTransformer(ASTTransformer):
    """Remove a class from the code.

    Args:
        tree (ast.Module): AST tree of the code.
        class_name (str): the name of the class to remove.
    """

    def __init__(self, tree: ast.Module, class_name: str):
        super().__init__(tree)
        self.class_name = class_name
        self.removed_node = None

    def visit_ClassDef(self, node):
        if node.name == self.class_name:
            self.removed_node = node
            return None
        return node


class MoveMethodToClassEndTransformer(ASTTransformer):
    """Move a method to the end of a class in the code.

    Args:
        tree (ast.Module): AST tree of the code.
        class_name (str): the name of the class.
        method_name (str): the name of the method to move.
    """

    def __init__(self, tree: ast.Module, class_name: str, method_name: str):
        super().__init__(tree)
        self.class_name = class_name
        self.method_name = method_name

    def visit_ClassDef(self, node):
        if node.name == self.class_name:
            method_to_move = None
            for method in node.body:
                if (
                    isinstance(method, ast.FunctionDef)
                    and method.name == self.method_name
                ):
                    method_to_move = method
                    break
            if method_to_move:
                node.body.remove(method_to_move)
                node.body.append(method_to_move)
        return node


class RemoveLastNodeTransformer(ASTTransformer):
    """Remove the last ast node from code.

    Args:
        tree (ast.Module): AST tree of the code.
    """

    def __init__(self, tree: ast.Module):
        super().__init__(tree)

    def visit_Module(self, node):

        if isinstance(node.body[-1], ast.ClassDef):
            if len(node.body[-1].body) == 1:
                node.body.pop()
            else:
                node.body[-1].body.pop()
        else:
            node.body.pop()

        return node


class RemoveMethodsTransformer(ASTTransformer):
    """Remove methods from a class in the code.

    Args:
        tree (ast.Module): AST tree of the code.
        method_names (list[str]): list of method names to remove.
    """

    def __init__(self, tree: ast.Module, method_names: list[str]):
        self.method_names = method_names
        super().__init__(tree)

    def visit_ClassDef(self, node):
        node.body = [
            method
            for method in node.body
            if not (
                isinstance(method, ast.FunctionDef) and method.name in self.method_names
            )
        ]
        return node
