import os
import rpyc
import socket
import random
import traceback
import subprocess
from time import sleep
from pathlib import Path

import fire

from r2e.paths import REPOS_DIR, TESTGEN_DIR, EXECUTION_DIR
from r2e.multiprocess import run_tasks_in_parallel_iter
from r2e.execution.execution_args import ExecutionArgs
from r2e.execution.r2e_simulator import DockerSimulator
from r2e.execution.execute_futs import self_equiv_futs
from r2e.models import FunctionUnderTest, MethodUnderTest
from r2e.utils.data import load_functions_under_test, write_functions_under_test


def find_free_ports(num_ports, start=49152, end=65535):
    free_ports = []
    for port in range(start, end):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("", port))
                free_ports.append(port)
                if len(free_ports) == num_ports:
                    return free_ports
            except OSError:
                continue
    raise RuntimeError(f"Could not find {num_ports} free ports in the specified range")


def start_server(repo_id: str, port: int):
    command = f"cd {REPOS_DIR}/{repo_id} && . .venv/bin/activate && r2e-test-server start --port {port} &"
    subprocess.Popen(command, shell=True)
    print(f"left {repo_id}...")


def stop_server(repo_id: str):
    command = (
        f"cd {REPOS_DIR}/{repo_id} && . .venv/bin/activate && r2e-test-server stop"
    )
    subprocess.Popen(command, shell=True)
    print(f"left {repo_id}...")


def get_service(repo_id: str, port: int) -> tuple[DockerSimulator, rpyc.Connection]:
    # simulator = DockerSimulator(repo_id=repo_id, port=port)
    start_server(repo_id, port)
    sleep(20)
    try:
        conn = rpyc.connect(
            "localhost", port, keepalive=True, config={"sync_request_timeout": 180}
        )
    except Exception as e:
        print(f"Connection error -- {repo_id} -- {repr(e)}")
        # simulator.stop_container()
        raise e
    return None, conn


def run_fut_with_port(
    fut: FunctionUnderTest | MethodUnderTest, port: int
) -> tuple[bool, str, FunctionUnderTest | MethodUnderTest]:
    try:
        simulator, conn = get_service(fut.repo_id, port)
    except Exception as e:
        print("Service error@", fut.repo_id, repr(e))
        fut.test_history.update_exec_stats({"error": repr(e)})
        return False, repr(e), fut
    try:
        return self_equiv_futs([fut], conn)
    except Exception as e:
        tb = traceback.format_exc()
        print(tb)
        pass
    finally:
        # simulator.stop_container()
        stop_server(fut.repo_id)
        conn.close()

    fut.test_history.update_exec_stats({"error": tb})
    print(f"Error@{fut.repo_id}:\n{tb}")
    return False, tb, fut


def run_fut_mp(args) -> tuple[bool, str, FunctionUnderTest | MethodUnderTest]:
    fut: FunctionUnderTest | MethodUnderTest
    port: int
    fut, port = args

    ## TODO: selected a random port, can collide with other processes!
    port = random.randint(3000, 10000)
    output = run_fut_with_port(fut, port)
    return output


def run_self_equiv(exec_args: ExecutionArgs):
    futs = load_functions_under_test(
        TESTGEN_DIR / f"{exec_args.testgen_exp_id}_generate.json"
    )
    futs = [fut for fut in futs if os.path.exists(f"{REPOS_DIR}/{fut.repo_id}/.venv")]
    futs = futs[:100]

    ports = find_free_ports(len(futs))

    new_futs = []
    if exec_args.execution_multiprocess == 0:
        for fut, port in zip(futs, ports):
            print(fut.file_path)
            print(fut.function_name)
            try:
                output = run_fut_with_port(fut, port)
            except Exception as e:
                print(f"Error@{fut.repo_id}:\n{repr(e)}")
                tb = traceback.format_exc()
                print(tb)
                continue
            new_futs.append(output[2])
    else:
        outputs = run_tasks_in_parallel_iter(
            run_fut_mp,
            list(zip(futs, ports)),
            num_workers=exec_args.execution_multiprocess,
            timeout_per_task=exec_args.timeout_per_task,
            use_progress_bar=True,
        )
        for x in outputs:
            if x.is_success():
                new_futs.append(x.result[2])  # type: ignore
            else:
                print(f"Error: {x.exception_tb}")

    print(len(new_futs))
    print(TESTGEN_DIR / f"{exec_args.testgen_exp_id}_out.json")
    write_functions_under_test(
        new_futs, TESTGEN_DIR / f"{exec_args.testgen_exp_id}_out.json"
    )


if __name__ == "__main__":
    exec_args = fire.Fire(ExecutionArgs)
    EXECUTION_DIR.mkdir(parents=True, exist_ok=True)
    run_self_equiv(exec_args)
