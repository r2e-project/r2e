""" Utilities for running functions in parallel processes. """

import sys
import queue
import resource
import traceback
from typing import Any, Optional
from enum import Enum
import multiprocessing as mp
from concurrent.futures import TimeoutError
from typing import Callable, Any, Iterator

import attrs
import tqdm
from pebble import concurrent, ProcessPool, ProcessExpired
import platform


class FuncTimeoutError(TimeoutError):
    pass


def generate_queue() -> queue.Queue[Any]:
    """
    Generates a queue that can be shared amongst processes
    Returns:
        (multiprocessing.Queue): A queue instance
    """
    manager = mp.Manager()
    return manager.Queue()


QueueEmptyException = queue.Empty


def run_func_in_process(
    func: Callable,
    *args,
    _timeout: None | int = None,
    _use_spawn: bool = True,
    **kwargs,
):
    """
    Runs the provided function in a separate process with the supplied args
    and kwargs. The args, kwargs, and
    return values must all be pickle-able.
    Args:
        func: The function to run.
        *args: Positional args, if any.
        _timeout: A timeout to use for the function.
        _use_spawn: The 'spawn' multiprocess context is used.'fork' otherwise.
        **kwargs: Keyword args, if any.
    Returns:
        The result of executing the function.
    """
    mode = "spawn" if _use_spawn else "fork"
    c_func = concurrent.process(timeout=_timeout, context=mp.get_context(mode))(func)
    future = c_func(*args, **kwargs)

    try:
        result = future.result()
        return result

    except TimeoutError:
        raise FuncTimeoutError


class TaskRunStatus(Enum):
    SUCCESS = 0
    EXCEPTION = 1
    TIMEOUT = 2
    PROCESS_EXPIRED = 3


@attrs.define(eq=False, repr=False)
class TaskResult:
    status: TaskRunStatus

    result: None | Any = None
    exception_tb: None | str = None

    def is_success(self) -> bool:
        return self.status == TaskRunStatus.SUCCESS

    def is_timeout(self) -> bool:
        return self.status == TaskRunStatus.TIMEOUT

    def is_exception(self) -> bool:
        return self.status == TaskRunStatus.EXCEPTION

    def is_process_expired(self) -> bool:
        return self.status == TaskRunStatus.PROCESS_EXPIRED


def initializer(limit: int) -> None:
    """Set maximum amount of memory each worker process can allocate."""
    soft, hard = resource.getrlimit(resource.RLIMIT_AS)
    resource.setrlimit(resource.RLIMIT_AS, (limit, hard))


def run_tasks_in_parallel_iter(
    func: Callable,
    tasks: list[Any],
    num_workers: int = 2,
    timeout_per_task: None | int = None,
    use_progress_bar: bool = False,
    progress_bar_desc: None | str = None,
    max_tasks_per_worker: None | int = None,
    use_spawn: bool = True,
    max_mem: int = 1024 * 1024 * 1024 * 4,
) -> Iterator[TaskResult]:
    """
    Args:
        func: The function to run. The function must accept a single argument.
        tasks: A list of tasks i.e. arguments to func.
        num_workers: Maximum number of parallel workers.
        timeout_per_task: The timeout, in seconds, to use per task.
        use_progress_bar: Whether to use a progress bar. Default False.
        progress_bar_desc: String to display in the progress bar. Default None.
        max_tasks_per_worker: Maximum number of tasks assigned
        to a single process / worker. None means infinite.
            Use 1 to force a restart.
        use_spawn: The 'spawn' multiprocess context is used. 'fork' otherwise.
    Returns:
        A list of TaskResult objects, one per task.
    """

    mode = "spawn" if use_spawn else "fork"

    with ProcessPool(
        # initializer=initializer if platform.system() != "Darwin" else None,  # type: ignore
        max_workers=num_workers,
        max_tasks=0 if max_tasks_per_worker is None else max_tasks_per_worker,
        context=mp.get_context(mode),
        # initargs=None,#(max_mem,) if platform.system() != "Darwin" else None,  # type: ignore
    ) as pool:
        future = pool.map(func, tasks, timeout=timeout_per_task)

        iterator = future.result()
        if use_progress_bar:
            pbar = tqdm.tqdm(
                desc=progress_bar_desc,
                total=len(tasks),
                dynamic_ncols=True,
            )
        else:
            pbar = None

        succ = timeouts = exceptions = expirations = 0

        while True:
            try:
                result = next(iterator)

            except StopIteration:
                break

            except TimeoutError as error:
                yield TaskResult(
                    status=TaskRunStatus.TIMEOUT,
                )

                timeouts += 1

            except ProcessExpired as error:
                yield TaskResult(
                    status=TaskRunStatus.PROCESS_EXPIRED,
                )
                expirations += 1

            except Exception as error:
                exception_tb = traceback.format_exc()

                yield TaskResult(
                    status=TaskRunStatus.EXCEPTION,
                    exception_tb=exception_tb,
                )
                exceptions += 1

            else:
                yield TaskResult(
                    status=TaskRunStatus.SUCCESS,
                    result=result,
                )

                succ += 1

            if pbar is not None:
                pbar.update(1)
                pbar.set_postfix(
                    succ=succ, timeouts=timeouts, exc=exceptions, p_exp=expirations
                )
                sys.stdout.flush()
                sys.stderr.flush()


def run_tasks_in_parallel(
    func: Callable,
    tasks: list[Any],
    num_workers: int = 2,
    timeout_per_task: None | int = None,
    use_progress_bar: bool = False,
    progress_bar_desc: None | str = None,
    max_tasks_per_worker: None | int = None,
    use_spawn: bool = True,
) -> list[TaskResult]:
    """
    Args:
        func: The function to run. The function must accept a single argument.
        tasks: A list of tasks i.e. arguments to func.
        num_workers: Maximum number of parallel workers.
        timeout_per_task: The timeout, in seconds, to use per task.
        use_progress_bar: Whether to use a progress bar. Defaults False.
        progress_bar_desc: String to display in the progress bar. Default None.
        max_tasks_per_worker: Maximum number of tasks assigned to a single
        process / worker. None means infinite.
            Use 1 to force a restart.
        use_spawn: The 'spawn' multiprocess context is used. 'fork' otherwise.
    Returns:
        A list of TaskResult objects, one per task.
    """

    task_results: list[TaskResult] = list(
        run_tasks_in_parallel_iter(
            func=func,
            tasks=tasks,
            num_workers=num_workers,
            timeout_per_task=timeout_per_task,
            use_progress_bar=use_progress_bar,
            progress_bar_desc=progress_bar_desc,
            max_tasks_per_worker=max_tasks_per_worker,
            use_spawn=use_spawn,
        )
    )

    return task_results
