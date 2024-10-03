from typing import Any, Optional
from pydantic import BaseModel


class Tests(BaseModel):
    tests: dict[str, str]
    operation: str = "generate"
    gen_model: Optional[str] = None
    gen_date: Optional[str] = None
    exec_stats: Optional[dict[str, Any]] = None

    def add(self, test_id: str, test: str):
        """Add a test to the tests"""
        self.tests[test_id] = test

    def update_stats(self, stats: dict[str, Any]):
        """Update the execution stats of the tests"""
        self.exec_stats = stats


class TestHistory(BaseModel):
    history: list[Tests] = []

    def add(self, tests: Tests):
        """Add tests to the history"""
        self.history.append(tests)

    def update_exec_stats(self, stats: dict[str, Any]):
        """Update the stats of the latest tests"""
        self.history[-1].update_stats(stats)

    @property
    def latest_operation(self) -> str:
        return self.history[-1].operation

    @property
    def latest_tests(self) -> dict[str, str]:
        return self.history[-1].tests

    @property
    def latest_exec_stats(self) -> Optional[dict[str, Any]]:
        return self.history[-1].exec_stats

    @property
    def is_passing(self) -> bool:
        """Returns True if the latest tests are passing"""
        if len(self.history) == 0:
            return False
        last_tests = self.history[-1]
        if last_tests.exec_stats is None:
            return False
        if "run_tests_logs" not in last_tests.exec_stats:
            return False
        last_tests_logs = last_tests.exec_stats["run_tests_logs"]
        last_tests_valid = all(logs["valid"] for logs in last_tests_logs.values())

        return last_tests_valid
