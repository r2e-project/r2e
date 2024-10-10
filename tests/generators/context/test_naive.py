import unittest

from r2e.generators.context import ContextCreator
from r2e.utils.data import load_functions
from r2e.paths import INTERESTING_FUNCS_DIR

ALL_FUNCTIONS_PATH = INTERESTING_FUNCS_DIR / "all_interesting.json"
ALL_FUNCTIONS = (
    load_functions(ALL_FUNCTIONS_PATH) if ALL_FUNCTIONS_PATH.exists() else []
)


@unittest.skipIf(not ALL_FUNCTIONS_PATH.exists(), "ALL_FUNCTIONS_PATH not found")
class TestNaiveContextCreator(unittest.TestCase):

    def test_naive_context(self):
        function = [
            f for f in ALL_FUNCTIONS if f.id == "klongpy.monads.eval_monad_range"
        ][0]

        context_creator = ContextCreator(function, 6000)
        context_creator.construct_context()
        naive_context = context_creator.get_context()

        self.assertEqual(naive_context.context.count("```python"), 1)
        self.assertIn("eval_monad_range", naive_context.context)
        self.assertEqual(naive_context.context.count("def "), 1)


if __name__ == "__main__":
    unittest.main()
