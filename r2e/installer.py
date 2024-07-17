import os

# 1. Extract tests from all repos
command = "python r2e/repo_builder/extract_func_methods.py"
os.system(command)

# 2. Generate 5-10 tests for each repo (you don't need any more than that)
command = "python r2e/generators/testgen/generate.py -i temp_extracted.json --max_tests=5"

# 3. Initiate the docker feedback loop

# 4. Move on to subsequent reop
