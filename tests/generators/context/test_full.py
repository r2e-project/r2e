import unittest

from r2e.generators.context import FullContextCreator, ContextFormat
from r2e.utils.data import load_functions
from r2e.paths import INTERESTING_FUNCS_DIR

ALL_FUNCTIONS_PATH = INTERESTING_FUNCS_DIR / "all_interesting.json"
ALL_FUNCTIONS = load_functions(ALL_FUNCTIONS_PATH)


class TestFullContextCreator(unittest.TestCase):

    def test_full_context_called(self):
        function = [
            f for f in ALL_FUNCTIONS if f.id == "klongpy.monads.eval_monad_range"
        ][0]

        function.repo.repo_id = function.repo.local_repo_path.split("/")[-1]
        context_creator = FullContextCreator(function, 6000)
        full_context = context_creator.get_context()

        self.assertEqual(full_context.context.count("```python"), 2)
        self.assertIn("create_monad_functions", full_context.context)

    def test_full_context_imported(self):
        function = [
            f for f in ALL_FUNCTIONS if f.id == "klongpy.monads.eval_monad_range"
        ][0]

        context_creator = FullContextCreator(function, 6000, filter_calls=False)
        full_context = context_creator.get_context()

        self.assertEqual(full_context.context.count("```python"), 2)
        self.assertIn("create_monad_functions", full_context.context)

    def test_full_context_called_path_comment_format(self):
        function = [
            f for f in ALL_FUNCTIONS if f.id == "klongpy.monads.eval_monad_range"
        ][0]

        context_creator = FullContextCreator(
            function, 6000, format=ContextFormat.PATH_COMMENT
        )
        full_context = context_creator.get_context()

        self.assertEqual(full_context.context.count("```python"), 0)
        self.assertEqual(full_context.context.count("# klongpy/"), 2)
        self.assertIn("# klongpy/core.py", full_context.context)
        self.assertIn("# klongpy/monads.py", full_context.context)
        self.assertIn("create_monad_functions", full_context.context)


if __name__ == "__main__":
    unittest.main()
