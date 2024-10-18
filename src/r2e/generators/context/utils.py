from r2e.generators.context.manager import ContextManager
from r2e.models.context import Context


def get_context_wrapper(args) -> Context:
    """A wrapper over ContextManager.get_context to be used in parallel processing"""
    context_type, func_meth, max_context_size = args
    return ContextManager.get_context(context_type, func_meth, max_context_size)
