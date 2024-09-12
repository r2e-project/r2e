# Demo: How to use R2E on your local repository?

#### Prerequisites

1. `r2e` is cloned and installed.
   
    ```bash
    git clone https://github.com/r2e-project/r2e.git
    cd r2e
    pip install -e . // or poetry install
    ```

2. `r2e-test-server` is installed

    ```bash
    pip install r2e-test-server
    ```

#### Steps to setup R2E and Equivalence tests

1. Setup your local repository (clone and install)
2. Let R2E extract functions and methods
3. Generate equivalence tests using R2E

> [!Note]
>
> To simplify exploration, we have wrapped the above steps in a single script for this demo. You can run the following command to execute the above steps: 
> `sh demos/setup.sh -u <REPO_URL> -p <LOCAL_REPO_PATH> -e <EXP_ID>`
>
> You can view the individual steps in the [setup.sh](/demos/setup.sh) script.


#### Steps to Execute and Evaluate tasks like code generation, refactoring, optimization, etc.

1. Start the r2e-test-server in a terminal

    ```bash
    r2e-test-server start
    ```

2. Communicate with the server using APIs. The steps are as follows:

    1. Load the generated equivalence tests from disk
    2. Pick a function under test
    3. Initialize the function, tests, and repo w/ the server
    4. Execute either the tests on existing (or) on modified code

> [!Note]
>
> To simplify exploration, we have wrapped the above steps in a single script for this demo. In this script, we will refactor a function and run the equivalence tests to ensure correctness. View the [refactor.py](/demos/refactor/refactor.py) script for more details.
>
> You can run the following command to execute the above steps: 
>
> `python demos/refactor/refactor.py`

When you run the above script, you will see output like the following:

```bash
......
----------------------------------------------------------------------
Ran 6 tests in 0.020s

OK
debug(refactored code): finding dependency globals
debug(refactored code): collecting globals
debug(refactored code): filtering globals
...
{
    "run_tests_logs": {
        "test_0": {
            "valid": true,
            "passed_count": 6,
            "passed_names": [
                "test_async_function",
                "test_class_method",
                "test_function_with_annotations",
                "test_function_with_builtins",
                "test_simple_function",
                "test_unique_flag"
            ],
            "failed_count": 0,
            "failed_names": [],
            "errored_count": 0,
            "errored_names": [],
            "skipped_count": 0,
            "expected_failures": 0,
            "unexpected_successes": 0
        }
    },
    "coverage_logs": [
        {}
    ]
}
```

- The debug statements indicate that the server is truly running the tests on the refactored code. The original code does not have any debug statements.
- The output shows that all the tests passed successfully => valid refactor.
- Change the functionality of the refactoring and see the tests fail.