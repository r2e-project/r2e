import ast
import tiktoken
from typing import Optional

from r2e.models.function import Function
from r2e.models.method import Method
from r2e.models.context import Context
from r2e.generators.context.format import ContextFormatter, ContextFormat
from r2e.pat.ast.transformer import (
    RemoveFunctionTransformer,
    RemoveLastNodeTransformer,
    RemoveClassTransformer,
    MoveMethodToClassEndTransformer,
)


class ContextCreator:
    """Base class for creating context for a function or method

    Args:
        func_meth (Function | Method): Function or Method object
        max_context_size (int): Maximum context size in # of tokens
    """

    def __init__(
        self,
        func_meth: Function | Method,
        max_context_size: int | None = None,
        format: ContextFormat = ContextFormat.MARKDOWN_FILES,
    ):
        self.func_meth = func_meth
        self.repo_path = self.func_meth.repo.repo_path
        self.full_to_rel_path = lambda x: x.removeprefix(self.repo_path)[1:]
        self.max_context_size = max_context_size
        self.context_type = "naive"
        self.context = ""
        self.file2code = {}

        # TODO: eventually make the tokenizer an arg.
        self.token_model = "gpt-3.5-turbo"
        self.tokenizer = tiktoken.encoding_for_model(self.token_model)

        self.format = format

    @property
    def context_size(self) -> int:
        """Return the size of the current context"""
        return len(self.tokenizer.encode(self.context, disallowed_special=()))

    def get_context(self) -> Context:
        """Return the current context"""
        context_info = {
            "context_type": self.context_type,
            "context": self.context,
        }
        return Context(**context_info)

    def construct_context(self):
        """constructor for the context (type: naive)

        note: can be overridden by subclasses
        """
        fut_code = self.func_meth.code

        if isinstance(self.func_meth, Method):
            fut_code = self._keep_only_method_in_class(self.func_meth)

        self.context = ContextFormatter.format(
            fut_code,
            self.full_to_rel_path(self.func_meth.file_path),
            self.format,
        )

    def truncate_context(self):
        """Truncates context to max_context_size

        note: can be overridden by subclasses
        """

        assert self.file2code is not {}, "file2code map empty"

        self.truncate_external_context()

        assert self.max_context_size is not None
        if self.context_size > self.max_context_size:
            self.truncate_file_context()

    def truncate_external_context(self):
        """General truncation strategy for external context

        note: external_context = {code | code in files, code.file != func.file}
        note: can be overridden by subclasses
        """

        file2code_map = self.file2code.copy()
        fut_rel_path = self.full_to_rel_path(self.func_meth.file_path)
        fut_code = file2code_map.pop(fut_rel_path)

        # if method, move method to class end to focus on it
        if isinstance(self.func_meth, Method):
            fut_code = self._move_method_to_class_end(
                fut_code,
                self.func_meth.class_name,  # type: ignore
                self.func_meth.name,  # type: ignore
            )

        assert self.max_context_size is not None
        # until context size reaches limit or all files are removed
        while self.context_size > self.max_context_size and len(file2code_map) > 0:
            last_file = list(file2code_map.keys())[0]
            last_code = file2code_map[last_file]

            # if file is empty, remove it
            if ast.parse(last_code).body == []:
                file2code_map.pop(last_file)

            # else, remove the last ast node from file
            else:
                truncated_code = self._remove_last_ast_node(last_code)
                file2code_map[last_file] = f"{truncated_code}\n\n# ..."

            self.context = ""
            for rel_path, code in file2code_map.items():
                self.context += ContextFormatter.format(code, rel_path, self.format)

            self.context += ContextFormatter.format(fut_code, fut_rel_path, self.format)

    def truncate_file_context(self):
        """General truncation strategy for in-file context

        note: can be overridden by subclasses
        """

        fut_rel_path = self.full_to_rel_path(self.func_meth.file_path)
        code = self.file2code[fut_rel_path]

        assert self.func_meth.name is not None, "Function name not available"

        # pop the function / method's parent class from code to avoid duplicating
        code, func_class_code = self._remove_func_class_from_file(code, self.func_meth)

        # if method, move method to class end to focus on it
        if isinstance(self.func_meth, Method):
            func_class_code = self._move_method_to_class_end(
                func_class_code,
                self.func_meth.class_name,  # type: ignore
                self.func_meth.name,
            )

        assert self.max_context_size is not None
        # until context size reaches limit or all ast nodes are removed
        while self.context_size > self.max_context_size and ast.parse(code).body != []:
            code = self._remove_last_ast_node(code)  # remove last ast node

            # if file is empty, use func_class_code as context
            if ast.parse(code).body == []:
                self.context = ""
                self.context = ContextFormatter.format(
                    func_class_code, fut_rel_path, self.format
                )
                break
            else:
                code += "\n\n# ..."

            formatted_code = self._append_code(code, func_class_code)
            self.context = ContextFormatter.format(
                formatted_code, fut_rel_path, self.format
            )

    # helpers

    @staticmethod
    def _remove_func_class_from_file(
        code: str, func_meth: Function | Method
    ) -> tuple[str, str]:
        """Remove a func_meth from code.
            - For a method, remove the entire class.
            - For a function, remove the function.

        Returns:
            tuple[str, str]: cleaned code, removed code
        """
        tree = ast.parse(code)

        if isinstance(func_meth, Method):
            transformer = RemoveClassTransformer(tree, func_meth.class_name)  # type: ignore
        else:
            transformer = RemoveFunctionTransformer(tree, func_meth.name)  # type: ignore

        cleaned_tree = transformer.transform()
        removed_node = transformer.removed_node

        if removed_node is None:
            raise ValueError(f"Function {func_meth.name} not found in code")

        return ast.unparse(cleaned_tree), ast.unparse(removed_node)

    @staticmethod
    def _append_code(code: str, removed_code: str) -> str:
        """Add removed code to the end of code"""
        return f"{code}\n\n{removed_code.strip()}\n"

    @staticmethod
    def _remove_last_ast_node(code: str) -> str:
        """Remove the last ast node from code"""
        tree = ast.parse(code)
        cleaned_tree = RemoveLastNodeTransformer(tree).transform()
        return ast.unparse(cleaned_tree)

    @staticmethod
    def _move_method_to_class_end(code: str, class_name: str, method_name: str) -> str:
        """Move a method to the end of a class"""
        tree = ast.parse(code)
        transformer = MoveMethodToClassEndTransformer(tree, class_name, method_name)
        cleaned_tree = transformer.transform()
        return ast.unparse(cleaned_tree)

    @staticmethod
    def _keep_only_method_in_class(method: Method) -> str:
        """Keep only the method in the class"""
        class_name = method.class_name
        method_name = method.name
        file_path = method.file.file_path

        with open(file_path, "r") as f:
            code = f.read()
            tree = ast.parse(code)

        class_node = None
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                class_node = node
                break

        if class_node is None:
            raise ValueError(f"Class {class_name} not found for method {method_name}")

        class_node.body = [
            method
            for method in class_node.body
            if isinstance(method, ast.FunctionDef) and method.name == method_name
        ]
        class_node.body.append(ast.Expr(ast.Str("# ...")))

        return ast.unparse(class_node)
