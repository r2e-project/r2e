import ast

from r2e.pat.ast import build_ast_file
from r2e.repo_builder.repo_args import RepoArgs
from r2e.repo_builder.fut_extractor.extract_base import FileBaseExtractor


class FileMethodExtractor(FileBaseExtractor):

    @staticmethod
    def extract_methods_from_ast(
        astree: ast.Module, repo_args: RepoArgs
    ) -> list[ast.FunctionDef]:
        method_asts = FileMethodExtractor.get_methods_from_ast(astree)

        if not repo_args.disable_all_filters:
            return method_asts

        ## remove dunder methods
        if not repo_args.disable_dunder_methods:
            method_asts = FileMethodExtractor.filter_dunder_methods(method_asts)

        ## remove methods without docstrings
        if not repo_args.disable_no_docstring:
            method_asts = FileMethodExtractor.filter_keep_docstring(method_asts)

        ## remove methods with literal returns
        if not repo_args.disable_signature_filters:
            method_asts = FileMethodExtractor.filter_literal_returns(method_asts)

        ## keyword filters and bad function names
        if not repo_args.disable_keyword_filters:
            method_asts = FileMethodExtractor.filter_docstring_keywords(method_asts)
            method_asts = FileMethodExtractor.filter_func_body_keywords(method_asts)
            method_asts = FileMethodExtractor.filter_bad_function_names(method_asts)

        ## remove wrapper and decorated methods
        if not repo_args.disable_wrapper_filters:
            method_asts = FileMethodExtractor.filter_with_decorator(
                method_asts, allowed_decorators=["staticmethod", "classmethod"]
            )
            method_asts = FileMethodExtractor.filter_wrapper_methods(method_asts)

        return method_asts

    @staticmethod
    def get_methods_from_ast(astree: ast.Module) -> list[ast.FunctionDef]:
        methods: list[ast.FunctionDef] = []
        for node in astree.body:
            if isinstance(node, ast.ClassDef):
                for subnode in node.body:
                    if isinstance(subnode, ast.FunctionDef):
                        methods.append(subnode)
        return methods

    @staticmethod
    def filter_wrapper_methods(
        method_asts: list[ast.FunctionDef],
    ) -> list[ast.FunctionDef]:
        return [
            method_ast
            for method_ast in method_asts
            if not FileMethodExtractor.is_wrapper_method(method_ast)
        ]

    @staticmethod
    def is_wrapper_method(method_ast: ast.FunctionDef) -> bool:
        if len(method_ast.body) == 1:
            return True
        if len(method_ast.body) == 2:
            if "self." in ast.unparse(method_ast.body[1]):
                return True
        if len(method_ast.body) == 3:
            if "self." in ast.unparse(method_ast.body[1]):
                if "return" in ast.unparse(method_ast.body[2]):
                    return True
        return False
