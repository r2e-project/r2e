import fire
from tqdm import tqdm
import traceback

from r2e.paths import *
from r2e.models import *
from r2e.utils.data import *
from r2e.multiprocess import run_tasks_in_parallel_iter

from r2e.execution.args import ExecutionArgs
from r2e.execution.service import ServiceManager
from r2e.execution.helpers import run_fut_with_port, run_fut_with_port_mp


class EquivalenceTestRunner:
    @staticmethod
    def run(args):
        """Run equivalence tests for functions"""
        futs = load_functions_under_test(TESTGEN_DIR / args.in_file)
        futs = futs[:1]
        print(f"Loaded {len(futs)} functions under test")

        new_futs = []
        if args.execution_multiprocess == 0:
            new_futs = EquivalenceTestRunner._run_futs_sequential(futs, args)
        else:
            new_futs = EquivalenceTestRunner._run_futs_parallel(futs, args)

        ServiceManager.shutdown()
        write_functions_under_test(new_futs, EXECUTION_DIR / f"{args.exp_id}_out.json")

    @staticmethod
    def _run_futs_sequential(futs, args):
        new_futs = []
        for i, fut in tqdm(enumerate(futs), desc="Running tests", total=len(futs)):
            port = args.port
            local = args.local
            image = args.image
            try:
                output = run_fut_with_port(fut, port, local, image, reuse_port=True)
            except Exception as e:
                print(f"Error@{fut.repo_id}:\n{repr(e)}")
                tb = traceback.format_exc()
                print(tb)
                continue
            new_futs.append(output[2])

            if (i + 1) % 20 == 0:
                write_functions_under_test(
                    new_futs, EXECUTION_DIR / f"{args.exp_id}_out.json"
                )

        return new_futs

    @staticmethod
    def _run_futs_parallel(futs, args):
        new_futs = []

        for i in range(0, len(futs), args.batch_size):
            batch = [(f, args.local, args.image) for f in futs[i : i + args.batch_size]]

            outputs = run_tasks_in_parallel_iter(
                run_fut_with_port_mp,
                batch,
                num_workers=args.execution_multiprocess,
                timeout_per_task=args.timeout_per_task,
                use_progress_bar=True,
            )

            for o in outputs:
                if o.is_success():
                    new_futs.append(o.result[2])  # type: ignore
                else:
                    print(f"Error: {o.exception_tb}")

            ServiceManager.shutdown()
            write_functions_under_test(
                new_futs, EXECUTION_DIR / f"{args.exp_id}_out.json"
            )

        return new_futs


if __name__ == "__main__":
    exec_args = fire.Fire(ExecutionArgs)
    EXECUTION_DIR.mkdir(parents=True, exist_ok=True)
    EquivalenceTestRunner.run(exec_args)
