# R2E Quickstart Guide (Local Usage)

This guide will help you get started with R2E quickly using local execution.

## Prerequisites

1. Ensure `r2e` is cloned and installed:
   
   ```bash
   git clone https://github.com/r2e-project/r2e.git
   cd r2e
   pip install -e .  # or poetry install
   ```

2. Install `r2e-test-server`:

   ```bash
   pip install r2e-test-server
   ```

## Setup R2E and Generate Equivalence Tests

We've simplified the setup process with a script. Run the following command:

```bash
sh demos/setup.sh -u <REPO_URL> -p <LOCAL_REPO_PATH> -e <EXP_ID>
```

This script performs the following steps:
1. Sets up your local repository (clone and install)
2. Extracts functions and methods using R2E
3. Generates equivalence tests using R2E

> [!Note]
> You can view the individual steps in the [setup.sh](/demos/setup.sh) script.

## Execute and Evaluate Tasks

1. Start the r2e-test-server in a terminal:
   ```bash
   r2e-test-server start
   ```

2. Run the demo script for task execution (e.g., refactoring):
   ```bash
   python demos/refactor/refactor.py
   ```

This script demonstrates how to:
1. Load generated equivalence tests
2. Pick a function under test
3. Initialize the function, tests, and repo with the server
4. Execute tests on existing or modified code

> [!Note]
> View the [refactor.py](/demos/refactor/refactor.py) script for more details on the execution process.

## Next Steps

For more advanced usage and full functionality with Docker, please refer to our [Full Guide](full_guide.md).