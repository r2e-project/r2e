from enum import Enum


class ContextFormat(Enum):
    MARKDOWN_FILES = "markdown_files"
    PATH_COMMENT = "path_comment"


class ContextFormatter:
    _format_methods = {
        ContextFormat.MARKDOWN_FILES: "_to_markdown_files",
        ContextFormat.PATH_COMMENT: "_to_path_comment",
    }

    @classmethod
    def format(cls, code: str, file_path: str, format_type: ContextFormat) -> str:
        """Formats the code based on the specified format type.

        Args:
            code (str): Code of the file
            file_path (str): Path of the file
            format_type (ContextFormat): Format to convert to

        Returns:
            str: Formatted code
        """
        method_name = cls._format_methods.get(format_type)

        if method_name is None:
            raise ValueError(f"Unsupported format: {format_type}")

        method = getattr(cls, method_name)
        return method(code, file_path)

    @staticmethod
    def _to_markdown_files(code: str, file_path: str) -> str:
        """
        Formats the code as a markdown file.
        """
        return f"```python\n# {file_path}\n\n{code}\n```\n"

    @staticmethod
    def _to_path_comment(code: str, file_path: str) -> str:
        """
        Formats the code with the file path as a comment.
        """
        return f"# {file_path}\n\n{code}\n"
