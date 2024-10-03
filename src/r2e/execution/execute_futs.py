import json
import rpyc
from collections import ChainMap

from r2e.models import FunctionUnderTest, MethodUnderTest


def setup_futs(
    futs: list[FunctionUnderTest | MethodUnderTest], service_client
) -> tuple[bool, str]:
    """
    Setups up the futs in the test server (via the service client)
    Involves sending repo, function and generated_tests to the server
    Returns a boolean based on success of the setup
        for codegen_mode it should always be true
        even for codegen_mode
    """

    repos = {fut.repo for fut in futs}
    assert len(repos) == 1, "All functions must belong to the same repo"

    repo = repos.pop()
    repo_data = json.dumps(repo.execution_repo_data)

    fut_data = [fut.execution_fut_data for fut in futs]
    fut_names = [x[0] for x in fut_data]
    fut_files = {x[1] for x in fut_data}

    assert len(fut_files) == 1, "All functions must belong to the same file"
    # print(fut_files, futs[0].execution_fut_data)

    fut_data = json.dumps({"funclass_names": fut_names, "file_path": fut_files.pop()})

    all_tests: dict[str, str] = dict(ChainMap(*[fut.tests for fut in futs]))
    test_data = json.dumps({"generated_tests": all_tests})

    service_client.setup_repo(repo_data)
    service_client.setup_function(fut_data)
    service_client.setup_test(test_data)

    init_response = service_client.init()
    init_error = str(init_response["error"])

    if init_error:
        futs[0].test_history.update_exec_stats(
            {
                "output": (
                    str(init_response["output"]) if "output" in init_response else None
                ),
                "error": init_error,
            }
        )
        return False, init_error
    else:
        return True, init_error


def self_equiv_futs(
    futs: list[FunctionUnderTest | MethodUnderTest], service_connection: rpyc.Connection
) -> tuple[bool, str, FunctionUnderTest | MethodUnderTest]:
    """
    Performs self-equivalence on the given futs via the service client
    NOTE: in case you only want to test top-level method
    wrap a sub-function `Function` or `Method` object as a
    `FunctionUnderTest` or `MethodUnderTest` object with empty tests

    It also stores the relevant metadata (captured I/O) in the futs (in place)

    Returns a boolean based on the success of the self-equivalence
    """
    service_client = service_connection.root
    assert service_client is not None, "Service client is None"
    init_success, init_error = setup_futs(futs, service_client)

    if not init_success:
        # print(init_response)
        return False, init_error, futs[0]

    submission_response = service_client.submit()

    if "logs" not in submission_response:
        # print(submission_response["error"])
        futs[0].test_history.update_exec_stats(
            {
                "error": str(submission_response["error"]),
            }
        )
        return False, str(submission_response["error"]), futs[0]
    submission_logs = json.loads(submission_response["logs"])

    valids = [x["valid"] for x in submission_logs["run_tests_logs"].values()]

    ## TODO -- support multiple futs
    futs[0].test_history.update_exec_stats(submission_logs)

    if not all(valids):
        return False, str(submission_response["error"]), futs[0]

    # print(True)

    return all(valids), str(submission_response["error"]), futs[0]
