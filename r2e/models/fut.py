from typing import Any, Optional

from pydantic import BaseModel

from r2e.models import Function, Method
from r2e.models.tests import TestHistory, Tests


class BaseUnderTest(BaseModel):
    test_history: TestHistory

    @property
    def tests(self) -> dict[str, str]:
        "Returns the latest tests for the function"
        return self.test_history.latest_tests

    @property
    def operation(self) -> str:
        "Returns the operation of the latest tests"
        return self.test_history.latest_operation

    @property
    def exec_stats(self) -> Optional[dict[str, Any]]:
        "Returns the execution stats of the latest tests"
        return self.test_history.latest_exec_stats

    def update_history(self, tests: Tests):
        """Update the test history of the function with new tests"""
        self.test_history.add(tests)

    def update_exec_stats(self, stats: dict[str, Any]):
        """Update the execution stats of the latest tests"""
        self.test_history.update_exec_stats(stats)

    @property
    def is_passing(self) -> bool:
        """Returns True if the latest tests are passing"""
        return self.test_history.is_passing


class FunctionUnderTest(BaseUnderTest, Function):
    @classmethod
    def from_function_and_history(
        cls, function: Function, history: Optional[TestHistory] = None
    ):
        if history is None:
            history = TestHistory()
        function_dump = function.model_dump()
        function_dump.update({"test_history": history})
        return cls(**function_dump)

    @classmethod
    def from_function(cls, function: Function):
        return cls.from_function_and_history(function)

    @property
    def execution_fut_data(self) -> tuple[str, str]:
        return f"{self.name}", self.file.relative_file_path


class MethodUnderTest(BaseUnderTest, Method):
    @classmethod
    def from_method_and_history(
        cls, method: Method, history: Optional[TestHistory] = None
    ):
        if history is None:
            history = TestHistory()
        method_dump = method.model_dump()
        method_dump.update({"test_history": history})
        return cls(**method_dump)

    @classmethod
    def from_method(cls, method: Method):
        return cls.from_method_and_history(method)

    @property
    def execution_fut_data(self) -> tuple[str, str]:
        return (
            f"{self.parent_class.class_name}.{self.name}",
            self.file.relative_file_path,
        )


# helper function


def create_code_under_test(obj: Function | Method):
    if isinstance(obj, Function):
        return FunctionUnderTest.from_function(obj)
    elif isinstance(obj, Method):
        return MethodUnderTest.from_method(obj)
    else:
        raise TypeError("obj must be a Function or Method instance")
