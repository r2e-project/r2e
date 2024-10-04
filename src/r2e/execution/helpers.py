import json
import rpyc
import random
import traceback

from r2e.models import FunctionUnderTest, MethodUnderTest
from r2e.execution.service import ServiceManager
from r2e.execution.utils import get_fut_data


def run_fut_with_port_mp(args) -> tuple[bool, str, FunctionUnderTest | MethodUnderTest]:
    fut: FunctionUnderTest | MethodUnderTest = args[0]
    local: bool = args[1]
    image: str = args[2]
    port = random.randint(3000, 10000)
    # note: cannot reuse_port for multiprocess
    output = run_fut_with_port(fut, port, local, image)
    return output


def run_fut_with_port(
    fut: FunctionUnderTest | MethodUnderTest,
    port: int,
    local: bool = False,
    image: str = "r2e:temp",
    reuse_port: bool = False,
) -> tuple[bool, str, FunctionUnderTest | MethodUnderTest]:
    try:
        simulator, conn = ServiceManager.get_service(fut.repo_id, port, local, image)
    except Exception as e:
        print("Service error@", fut.repo_id, repr(e))
        fut.test_history.update_exec_stats({"error": repr(e)})
        return False, repr(e), fut

    try:
        return self_equiv_futs([fut], conn, local)
    except Exception as e:
        tb = traceback.format_exc()
        pass
    finally:
        if simulator:
            simulator.stop_container()
        conn.close()
        if not reuse_port:
            ServiceManager.close_connection(port)

    fut.test_history.update_exec_stats({"error": tb})
    print(f"Error@{fut.repo_id}:\n{tb}")

    return False, tb, fut


def self_equiv_futs(
    futs: list[FunctionUnderTest | MethodUnderTest],
    conn: rpyc.Connection,
    local: bool = False,
) -> tuple[bool, str, FunctionUnderTest | MethodUnderTest]:
    """Executes equivalence tests for given futs via the service client

    NOTE: in case you only want to test top-level method
    wrap a sub-function `Function` or `Method` object as a
    `FunctionUnderTest` or `MethodUnderTest` object with empty tests

    It also stores the relevant metadata (captured I/O) in the futs (in place)

    Args:
        futs (list[FunctionUnderTest | MethodUnderTest]): list of functions under test
        conn (rpyc.Connection): connection to the service client

    Returns:
        tuple[bool, str, FunctionUnderTest | MethodUnderTest]: success, error, fut
    """
    service = conn.root
    assert service is not None, "Test service is None"

    repo_data, fut_data, test_data = get_fut_data(futs, local=local)

    ####### Setup the service #######
    service.setup_repo(repo_data)
    service.setup_function(fut_data)
    service.setup_test(test_data)

    init_response = service.init()
    init_output = str(init_response["output"])
    init_error = str(init_response["error"])

    # NOTE hacks to ignore invalid errors:
    # - escapes in docstrings / nameerors due to type_checking=false
    # TODO remove once python versions are set according to repo)
    ignore_patterns = ["SyntaxWarning: invalid escape sequence", "NameError: "]

    if init_error and not any(p in init_error for p in ignore_patterns):
        futs[0].test_history.update_exec_stats(
            {"output": init_output, "error": init_error}
        )
        print(f"Init Error@{futs[0].id}:\n{init_error}\n\n")
        return False, init_error, futs[0]

    ####### Execute the equivalence test #######

    try:
        submit_response = service.submit()
    except Exception as e:
        futs[0].test_history.update_exec_stats({"error": repr(e)})
        print(f"Submit Error@{futs[0].id}:\n{repr(e)}\n\n")
        return False, repr(e), futs[0]

    submit_error = str(submit_response["error"])

    if "logs" not in submit_response:
        futs[0].test_history.update_exec_stats({"error": submit_error})
        print(f"Submit Error@{futs[0].id}:\n{submit_error}\n\n")
        return False, submit_error, futs[0]

    submit_logs = json.loads(submit_response["logs"])
    submit_logs["output"] = submit_response["output"]
    futs[0].test_history.update_exec_stats(submit_logs)

    valids = [x["valid"] for x in submit_logs["run_tests_logs"].values()]
    return all(valids), submit_error, futs[0]
