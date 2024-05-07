import ast

import nltk

nltk.download("punkt", quiet=True)


class FileBaseExtractor:

    @staticmethod
    def filter_dunder_methods(
        function_asts: list[ast.FunctionDef],
    ) -> list[ast.FunctionDef]:
        return [
            function_ast
            for function_ast in function_asts
            if not function_ast.name.startswith("__")
        ]

    @staticmethod
    def filter_keep_docstring(
        function_asts: list[ast.FunctionDef],
    ) -> list[ast.FunctionDef]:
        return [
            function_ast
            for function_ast in function_asts
            if FileBaseExtractor.has_docstring(function_ast)
        ]

    @staticmethod
    def has_docstring(
        function_ast: ast.FunctionDef,
    ) -> bool:
        return ast.get_docstring(function_ast) is not None

    @staticmethod
    def filter_literal_returns(
        function_asts: list[ast.FunctionDef],
    ) -> list[ast.FunctionDef]:
        return [
            function_ast
            for function_ast in function_asts
            if not FileBaseExtractor.has_literal_return(function_ast)
        ]

    @staticmethod
    def has_literal_return(
        function_ast: ast.FunctionDef,
    ) -> bool:
        is_constant_return = [
            isinstance(node.value, ast.Constant)
            for node in function_ast.body
            if isinstance(node, ast.Return)
        ]
        return sum(is_constant_return) > 2 / 3 * len(
            is_constant_return
        )  ## 2/3 is an arbitrary threshold

    @staticmethod
    def filter_with_decorator(
        function_asts: list[ast.FunctionDef],
        allowed_decorators: list[str] = [],
    ) -> list[ast.FunctionDef]:
        return [
            function_ast
            for function_ast in function_asts
            if all(
                [
                    ast.unparse(x) in allowed_decorators
                    for x in function_ast.decorator_list
                ]
            )
        ]

    @staticmethod
    def filter_docstring_keywords(
        function_asts: list[ast.FunctionDef],
    ) -> list[ast.FunctionDef]:
        BAD_DOC_SUBSTRINGS = {
            "test",
            "transformer",
            "training",
            "https",
            "http",
            "todo",
        }
        return [
            function_ast
            for function_ast in function_asts
            if FileBaseExtractor.get_docstring_tokens_lowered(function_ast).isdisjoint(
                BAD_DOC_SUBSTRINGS
            )
        ]

    @staticmethod
    def get_docstring_tokens_lowered(
        function_ast: ast.FunctionDef,
    ) -> set[str]:
        body0_node = function_ast.body[0]
        assert isinstance(body0_node, ast.Expr)
        docstring_node = body0_node.value
        assert isinstance(docstring_node, ast.Constant)
        docstring = docstring_node.value
        assert isinstance(docstring, str)
        return {token.lower() for token in nltk.word_tokenize(docstring)}

    @staticmethod
    def filter_func_body_keywords(
        function_asts: list[ast.FunctionDef],
    ) -> list[ast.FunctionDef]:
        BAD_CODE_SUBSTRINGS = {
            "demo",
            "gcp",
            "s3",
            "openai",
            "aws",
            "cuda",
            "tensorflow",
            "triton",
            "gpu",
            "nvidia",
            "scheduler",
            "async",
            "job",
            "do_not_import",
            "do_not_run",
            "do_not_call",
            "plt",
            "plot",
            "matplotlib",
            "seaborn",
            "plotly",
            "argparse",
            "main",
            "cuda_visible_devices",
            "multiprocess",
            "multiprocessing",
            "pool",
            "processpool",
            "threadpool",
            "joblib",
            "pebble",
        }
        return [
            function_ast
            for function_ast in function_asts
            if FileBaseExtractor.get_func_body_tokens_lowered(function_ast).isdisjoint(
                BAD_CODE_SUBSTRINGS
            )
        ]

    @staticmethod
    def filter_func_substrings(
        function_asts: list[ast.FunctionDef],
    ):
        BAD_CODE_SUBSTRINGS = {
            "cuda",
            "gpu",
            "nvidia",
            "triton",
            "tensorflow",
            "multiprocess",
            "pool",
            "processpool",
            "threadpool",
            "joblib",
            "mp.",
        }
        return [
            function_ast
            for function_ast in function_asts
            if any(
                substring in ast.unparse(function_ast).lower()
                for substring in BAD_CODE_SUBSTRINGS
            )
        ]

    @staticmethod
    def get_func_body_tokens_lowered(
        function_ast: ast.FunctionDef,
    ) -> set[str]:
        tokens = set()
        for node in ast.walk(function_ast):
            if isinstance(node, ast.Name):
                tokens.add(node.id.lower())
            elif isinstance(node, ast.Constant):
                tokens.add(str(node.value).lower())
        return tokens

    @staticmethod
    def filter_bad_function_names(
        function_asts: list[ast.FunctionDef],
    ) -> list[ast.FunctionDef]:
        return [
            function_ast
            for function_ast in function_asts
            if not FileBaseExtractor.filter_bad_function_name(function_ast)
        ]

    @staticmethod
    def filter_bad_function_name(
        function_ast: ast.FunctionDef,
    ) -> bool:
        BAD_FUNCTION_NAME_PREFIXES = {
            "test",
            "train_",
            "main",
            "demo",
            "example",
            "render_pep",
            "_init",
        }
        return any(
            function_ast.name.lower().startswith(prefix)
            for prefix in BAD_FUNCTION_NAME_PREFIXES
        )
