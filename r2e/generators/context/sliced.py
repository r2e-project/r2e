import io
import ast
import contextlib

from r2e.models import Function, Method
from r2e.generators.context.base import ContextCreator
from r2e.generators.context.format import ContextFormat
from r2e.pat.dependency_slicer import DependencySlicer, DependencySliceUnparseEnum


class SlicedContextCreator(ContextCreator):
    """Class for creating sliced context for a function or method

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
        super().__init__(func_meth, max_context_size, format)
        self.context_type = "sliced"
        self.construct_context()

    def construct_context(self):
        with contextlib.redirect_stdout(io.StringIO()):
            if isinstance(self.func_meth, Method):
                slicer = DependencySlicer.from_class_models(self.func_meth.parent_class)
            elif isinstance(self.func_meth, Function):
                slicer = DependencySlicer.from_function_models(self.func_meth)
            else:
                raise ValueError("Unknown input type")

            slicer.run()

            slice_format = DependencySliceUnparseEnum.MARKDOWN_FILES
            self.context = slicer.dependency_graph.unparse(unparse_type=slice_format)
            self.file2code = slicer.dependency_graph.unparse_by_file()

        # trigger truncation if necessary
        if self.max_context_size and self.context_size > self.max_context_size:
            self.truncate_context()
