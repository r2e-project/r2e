import json
import inspect
import functools


class Instrumenter:
    def __init__(self):
        self.current_frame = None
        self.previous_frame = None
        self.output = None
        pass

    def instrument(self, func):
        """Wrap the given function with the instrumentation logic."""

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            self.current_frame = inspect.currentframe()
            if self.current_frame is not None:
                self.previous_frame = self.current_frame.f_back

            self.before_call(func, *args, **kwargs)
            self.output = func(*args, **kwargs)
            self.after_call(func, *args, **kwargs)
            return self.output

        return wrapper

    def caller_info(self):
        """Return the caller's information."""
        if self.previous_frame is None:
            return None

        caller_info = inspect.getframeinfo(self.previous_frame)
        caller_info = {"func_name": caller_info[2], "lineno": caller_info[1]}
        return caller_info

    def before_call(self, func, *args, **kwargs):
        """Hook method for doing something before the original function call."""
        pass

    def after_call(self, func, *args, **kwargs):
        """Hook method for doing something after the original function call."""
        pass

    def dump_logs(self, file_path: str):
        """Dump the collected information, if any, to a file."""
        pass
