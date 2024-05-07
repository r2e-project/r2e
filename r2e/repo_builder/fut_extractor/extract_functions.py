import ast

from r2e.repo_builder.fut_extractor.extract_base import FileBaseExtractor


class FileFunctionExtractor(FileBaseExtractor):

    @staticmethod
    def extract_functions_from_ast(astree: ast.Module) -> list[ast.FunctionDef]:
        function_asts = FileFunctionExtractor.get_functions_from_ast(astree)

        ## remove dunder methods
        function_asts = FileFunctionExtractor.filter_dunder_methods(function_asts)

        ## remove functions without docstrings
        function_asts = FileFunctionExtractor.filter_keep_docstring(function_asts)

        ## remove functions without arguments
        function_asts = FileFunctionExtractor.filter_nonzero_arguments(function_asts)

        ## remove functions without returns
        function_asts = FileFunctionExtractor.filter_nonzero_returns(function_asts)

        ## remove functions with literal returns
        function_asts = FileFunctionExtractor.filter_literal_returns(function_asts)

        ## has_decorator
        function_asts = FileFunctionExtractor.filter_with_decorator(function_asts)

        ## keyword filters
        function_asts = FileFunctionExtractor.filter_docstring_keywords(function_asts)
        function_asts = FileFunctionExtractor.filter_func_body_keywords(function_asts)

        ## remove functions with bad function names
        function_asts = FileFunctionExtractor.filter_bad_function_names(function_asts)

        ## remove wrapper methods
        function_asts = FileFunctionExtractor.filter_onlt_one_stmt(function_asts)

        return function_asts

    @staticmethod
    def get_functions_from_ast(astree: ast.Module) -> list[ast.FunctionDef]:
        functions: list[ast.FunctionDef] = []
        for node in astree.body:
            if isinstance(node, ast.FunctionDef):
                functions.append(node)
        return functions

    @staticmethod
    def filter_nonzero_arguments(
        function_asts: list[ast.FunctionDef],
    ) -> list[ast.FunctionDef]:
        return [
            function_ast
            for function_ast in function_asts
            if FileFunctionExtractor.get_num_args(function_ast) > 0
        ]

    @staticmethod
    def get_num_args(function_ast: ast.FunctionDef) -> int:
        return (
            len(function_ast.args.args)
            + len(function_ast.args.kwonlyargs)
            + len(function_ast.args.posonlyargs)
            + (0 if function_ast.args.kwarg is None else 1)
            + (0 if function_ast.args.vararg is None else 1)
        )

    @staticmethod
    def filter_nonzero_returns(
        function_asts: list[ast.FunctionDef],
    ) -> list[ast.FunctionDef]:
        return [
            function_ast
            for function_ast in function_asts
            if any(isinstance(node, ast.Return) for node in function_ast.body)
        ]

    @staticmethod
    def filter_onlt_one_stmt(
        function_asts: list[ast.FunctionDef],
    ) -> list[ast.FunctionDef]:
        ## body[0] is docstring!
        return [
            function_ast for function_ast in function_asts if len(function_ast.body) > 2
        ]
