import unittest

from r2e.generators.context import SlicedContextCreator
from r2e.utils.data import load_functions
from r2e.paths import INTERESTING_FUNCS_DIR

ALL_FUNCTIONS_PATH = INTERESTING_FUNCS_DIR / "all_interesting.json"
ALL_FUNCTIONS = load_functions(ALL_FUNCTIONS_PATH)


class TestSlicedContextCreator(unittest.TestCase):

    def test_sliced_context(self):
        function = [
            f for f in ALL_FUNCTIONS if f.id == "klongpy.monads.eval_monad_range"
        ][0]
        function.repo.repo_id = function.repo.local_repo_path.split("/")[-1]
        context_creator = SlicedContextCreator(function, 6000)
        sliced_context = context_creator.get_context()

        self.assertEqual(sliced_context.context.count("```python"), 3)
        self.assertNotIn("create_monad_functions", sliced_context.context)
        self.assertIn("str_to_chr_arr", sliced_context.context)


if __name__ == "__main__":
    unittest.main()
