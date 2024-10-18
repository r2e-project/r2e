from r2e.models.function import Function
from r2e.models.method import Method
from r2e.models.context import Context
from r2e.generators.context import (
    ContextCreator,
    FullContextCreator,
    SlicedContextCreator,
)


class ContextManager:

    @staticmethod
    def get_context(
        context_type: str, func_meth: Function | Method, max_context_size: int
    ) -> Context:

        if context_type == "naive":
            nc = ContextCreator(func_meth, max_context_size)
            nc.construct_context()
            return nc.get_context()

        elif context_type == "full":
            return FullContextCreator(func_meth, max_context_size).get_context()

        elif context_type == "sliced":
            return SlicedContextCreator(func_meth, max_context_size).get_context()

        else:
            raise ValueError(f"Invalid context type: {context_type}")
